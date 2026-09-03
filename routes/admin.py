from flask import Blueprint, render_template, redirect, url_for, session, flash, request, jsonify
from utils.decorators import login_required, admin_required
from services import company_service
from models.user import User
from models.job import Job
from models.application import Application
from models.company import Company
from models.admin_security import (
    log_admin_activity, ACTION_COMPANY_APPROVED, ACTION_COMPANY_REJECTED,
    ACTION_COMPANY_DELETED, ACTION_USER_TOGGLED, ACTION_USER_MADE_ADMIN,
    ACTION_USER_REMOVED_ADMIN
)
from extensions import db

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@login_required
@admin_required
def panel():
    companies = Company.query.order_by(Company.created_at.desc()).all()
    stats = {
        'total_companies': Company.query.count(),
        'verified_companies': Company.query.filter_by(is_verified=True).count(),
        'pending_companies': Company.query.filter_by(verification_status='pending').count(),
        'total_users': User.query.count(),
        'total_jobs': Job.query.count(),
        'total_applications': Application.query.count(),
    }
    return render_template('index_admin.html', page='admin',
                         companies=companies,
                         stats=stats)


@bp.route('/verify-company/<company_id>', methods=['POST'])
@login_required
@admin_required
def verify_company(company_id):
    company_service.verify_company(company_id)
    log_admin_activity(str(session['user_id']), ACTION_COMPANY_APPROVED,
                       'company', company_id,
                       description=f'تم توثيق الشركة',
                       ip_address=request.remote_addr)
    flash('✅ تم توثيق الشركة بنجاح!', 'success')
    return redirect(url_for('admin.panel'))


@bp.route('/reject-company/<company_id>', methods=['POST'])
@login_required
@admin_required
def reject_company(company_id):
    company_service.reject_company(company_id)
    log_admin_activity(str(session['user_id']), ACTION_COMPANY_REJECTED,
                       'company', company_id,
                       description=f'تم رفض توثيق الشركة',
                       ip_address=request.remote_addr)
    flash('❌ تم رفض توثيق الشركة.', 'error')
    return redirect(url_for('admin.panel'))


@bp.route('/companies')
@login_required
@admin_required
def companies():
    companies_list = Company.query.order_by(Company.created_at.desc()).all()
    return render_template('index_admin_companies.html', page='admin_companies', companies=companies_list)


@bp.route('/company/<company_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_company(company_id):
    company = Company.query.get(company_id)
    if company:
        company_name = company.name
        Job.query.filter_by(company_id=company_id).delete()
        db.session.delete(company)
        db.session.commit()
        log_admin_activity(str(session['user_id']), ACTION_COMPANY_DELETED,
                           'company', company_id,
                           description=f'تم حذف الشركة: {company_name}',
                           ip_address=request.remote_addr)
    flash('🗑️ تم حذف الشركة بنجاح', 'success')
    return redirect(url_for('admin.companies'))


@bp.route('/users')
@login_required
@admin_required
def users():
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('index_admin_users.html', page='admin_users', users=users_list)


@bp.route('/user/<user_id>')
@login_required
@admin_required
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    profile = user.profile if hasattr(user, 'profile') else None
    jobs = []
    applications = []
    if user.user_type == 'employer':
        jobs = Job.query.filter_by(employer_id=user_id).all()
    elif user.user_type == 'job_seeker':
        applications = Application.query.filter_by(job_seeker_id=user_id).all()
    return render_template('index_admin_user_details.html', page='admin_user_details',
                         user=user, profile=profile, jobs=jobs, applications=applications)


@bp.route('/user/<user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    log_admin_activity(str(session['user_id']), ACTION_USER_TOGGLED,
                       'user', user_id,
                       description=f'{"تفعيل" if user.is_active else "تعطيل"} المستخدم',
                       ip_address=request.remote_addr)
    flash(f'✅ تم {"تفعيل" if user.is_active else "تعطيل"} المستخدم', 'success')
    return redirect(url_for('admin.user_details', user_id=user_id))


@bp.route('/user/<user_id>/make-admin', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    log_admin_activity(str(session['user_id']), ACTION_USER_MADE_ADMIN,
                       'user', user_id,
                       description=f'تعيين المستخدم كمدير',
                       ip_address=request.remote_addr)
    flash('✅ تم تعيين المستخدم كمدير', 'success')
    return redirect(url_for('admin.user_details', user_id=user_id))


@bp.route('/user/<user_id>/remove-admin', methods=['POST'])
@login_required
@admin_required
def remove_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == session['user_id']:
        flash('❌ لا يمكنك إزالة صلاحياتك الخاصة', 'error')
        return redirect(url_for('admin.user_details', user_id=user_id))
    user.is_admin = False
    db.session.commit()
    log_admin_activity(str(session['user_id']), ACTION_USER_REMOVED_ADMIN,
                       'user', user_id,
                       description=f'إزالة صلاحيات المدير',
                       ip_address=request.remote_addr)
    flash('✅ تم إزالة صلاحيات المدير', 'success')
    return redirect(url_for('admin.user_details', user_id=user_id))


@bp.route('/stats')
@login_required
@admin_required
def stats():
    from models.profile import Profile
    stats_data = {
        'total_users': User.query.count(),
        'job_seekers': User.query.filter_by(user_type='job_seeker').count(),
        'employers': User.query.filter_by(user_type='employer').count(),
        'total_companies': Company.query.count(),
        'verified_companies': Company.query.filter_by(is_verified=True).count(),
        'total_jobs': Job.query.count(),
        'active_jobs': Job.query.filter_by(is_active=True).count(),
        'total_applications': Application.query.count(),
    }
    return render_template('index_admin_stats.html', page='admin_stats', stats=stats_data)
