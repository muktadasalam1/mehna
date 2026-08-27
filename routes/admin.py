from flask import Blueprint, render_template, redirect, url_for, session, flash
from utils.decorators import login_required, admin_required
from services import company_service
from models.user import User
from models.job import Job
from models.application import Application
from models.company import Company
from extensions import db

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@login_required
@admin_required
def panel():
    pending_companies = company_service.get_pending_companies()
    verified_companies = company_service.get_verified_companies()
    rejected_companies = company_service.get_rejected_companies()

    stats = {
        'users': User.query.count(),
        'jobs': Job.query.filter_by(is_active=True).count(),
        'pending': Company.query.filter_by(verification_status='pending').count(),
        'companies': Company.query.count()
    }

    return render_template('index_admin.html', page='admin',
                         pending_companies=pending_companies,
                         verified_companies=verified_companies,
                         rejected_companies=rejected_companies,
                         stats=stats)


@bp.route('/verify-company/<company_id>')
@login_required
@admin_required
def verify_company(company_id):
    company_service.verify_company(company_id)
    flash('✅ تم توثيق الشركة بنجاح!', 'success')
    return redirect(url_for('admin.panel'))


@bp.route('/reject-company/<company_id>')
@login_required
@admin_required
def reject_company(company_id):
    company_service.reject_company(company_id)
    flash('❌ تم رفض توثيق الشركة.', 'error')
    return redirect(url_for('admin.panel'))


@bp.route('/companies')
@login_required
@admin_required
def companies():
    companies_list = company_service.get_all_companies()
    return render_template('index_admin_companies.html', page='admin_companies', companies=companies_list)


@bp.route('/company/<company_id>/delete')
@login_required
@admin_required
def delete_company(company_id):
    company = Company.query.get(company_id)
    if company:
        Job.query.filter_by(company_id=company_id).delete()
        db.session.delete(company)
        db.session.commit()
    flash('🗑️ تم حذف الشركة بنجاح', 'success')
    return redirect(url_for('admin.companies'))


@bp.route('/company/<company_id>/details')
@login_required
@admin_required
def company_details(company_id):
    stats = company_service.get_company_stats(company_id)
    if not stats:
        flash('الشركة غير موجودة', 'error')
        return redirect(url_for('admin.companies'))

    jobs = Job.query.filter_by(company_id=company_id).all()
    owner = User.query.join(Job, Job.employer_id == User.id).filter(Job.company_id == company_id).first()

    return render_template('index_admin_company_details.html', page='admin_company_details',
                         company=stats['company'], jobs=jobs, owner=owner)


@bp.route('/users')
@login_required
@admin_required
def users():
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('index_admin_users.html', page='admin_users', users=users_list)


@bp.route('/user/<user_id>/details')
@login_required
@admin_required
def user_details(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('المستخدم غير موجود', 'error')
        return redirect(url_for('admin.users'))

    from models.profile import Profile
    profile = Profile.query.filter_by(user_id=user_id).first()
    jobs = Job.query.filter_by(employer_id=user_id).all()
    applications = Application.query.filter_by(job_seeker_id=user_id).all()

    return render_template('index_admin_user_details.html', page='admin_user_details',
                         user=user, profile=profile, jobs=jobs, applications=applications)


@bp.route('/user/<user_id>/toggle')
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_active = not user.is_active
        db.session.commit()
    flash('تم تحديث حالة المستخدم', 'success')
    return redirect(url_for('admin.users'))


@bp.route('/user/<user_id>/make-admin')
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_admin = True
        db.session.commit()
    flash('تم جعل المستخدم أدمن', 'success')
    return redirect(url_for('admin.users'))


@bp.route('/user/<user_id>/remove-admin')
@login_required
@admin_required
def remove_admin(user_id):
    if str(user_id) == str(session['user_id']):
        flash('⚠️ لا يمكنك إزالة صلاحية الأدمن من حسابك الخاص!', 'error')
        return redirect(url_for('admin.users'))
    user = User.query.get(user_id)
    if user:
        user.is_admin = False
        db.session.commit()
    flash('تم إزالة صلاحية الأدمن', 'success')
    return redirect(url_for('admin.users'))


@bp.route('/stats')
@login_required
@admin_required
def stats():
    stats = {
        'total_users': User.query.count(),
        'total_employers': User.query.filter_by(user_type='employer').count(),
        'total_seekers': User.query.filter_by(user_type='job_seeker').count(),
        'total_jobs': Job.query.count(),
        'active_jobs': Job.query.filter_by(is_active=True).count(),
        'total_apps': Application.query.count(),
        'total_companies': Company.query.count(),
        'pending': Company.query.filter_by(verification_status='pending').count(),
        'verified': Company.query.filter_by(verification_status='verified').count(),
        'rejected': Company.query.filter_by(verification_status='rejected').count(),
        'top_jobs': Job.query.order_by(Job.views_count.desc()).limit(5).all()
    }
    return render_template('index_admin_stats.html', page='admin_stats', stats=stats)


@bp.route('/dashboard')
@login_required
@admin_required
def dashboard_full():
    stats = {
        'total_users': User.query.count(),
        'total_employers': User.query.filter_by(user_type='employer').count(),
        'total_seekers': User.query.filter_by(user_type='job_seeker').count(),
        'total_admins': User.query.filter_by(is_admin=True).count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_jobs': Job.query.count(),
        'active_jobs': Job.query.filter_by(is_active=True).count(),
        'closed_jobs': Job.query.filter_by(is_active=False).count(),
        'total_apps': Application.query.count(),
        'pending_apps': Application.query.filter_by(status='pending').count(),
        'accepted_apps': Application.query.filter_by(status='accepted').count(),
        'rejected_apps': Application.query.filter_by(status='rejected').count(),
        'total_companies': Company.query.count(),
        'pending_companies': Company.query.filter_by(verification_status='pending').count(),
        'verified_companies': Company.query.filter_by(verification_status='verified').count(),
        'rejected_companies': Company.query.filter_by(verification_status='rejected').count()
    }

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_jobs = db.session.query(Job, Company.name.label('company_name')).join(
        Company, Job.company_id == Company.id
    ).order_by(Job.created_at.desc()).limit(5).all()
    top_companies = db.session.query(
        Company.name, db.func.count(Job.id).label('jobs_count')
    ).join(Job, Company.id == Job.company_id).group_by(Company.id, Company.name).order_by(
        db.desc('jobs_count')
    ).limit(5).all()

    return render_template('index_admin_dashboard_full.html', page='admin_dashboard_full',
                         stats=stats, recent_users=recent_users,
                         recent_jobs=recent_jobs, top_companies=top_companies)
