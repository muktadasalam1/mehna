from flask import Blueprint, render_template, session, redirect, url_for, flash
from utils.decorators import login_required
from services import job_service, company_service, auth_service
from models.user import User
from models.profile import Profile
from models.job import Job
from models.company import Company
from models.application import Application
from extensions import db

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    jobs = job_service.get_active_jobs(limit=6)
    stats = {
        'jc': Job.query.filter_by(is_active=True).count(),
        'cc': Company.query.filter_by(is_verified=True).count(),
        'sc': User.query.filter_by(user_type='job_seeker').count()
    }
    return render_template('index_home.html', page='home', jobs=jobs, stats=stats)


@bp.route('/dashboard')
@login_required
def dashboard():
    if session.get('user_role') == 'admin':
        return redirect(url_for('admin.panel'))

    if session['user_role'] == 'job_seeker':
        profile = Profile.query.filter_by(user_id=session['user_id']).first()
        applications = Application.query.filter_by(job_seeker_id=session['user_id']).all()
        return render_template('index_dashboard.html', page='dashboard', profile=profile, applications=applications)
    else:
        companies = company_service.get_companies_by_employer(session['user_id'])
        my_company = company_service.get_company_by_employer(session['user_id'])

        can_request_verification = False
        verification_status = None
        if my_company:
            verification_status = my_company.verification_status
            if verification_status in ['rejected', None]:
                can_request_verification = True

        jobs_list = []
        if companies:
            ids = [str(x.id) for x in companies]
            if ids:
                jobs_list = Job.query.filter(
                    Job.company_id.in_([int(x) for x in ids])
                ).order_by(Job.created_at.desc()).all()

        return render_template('index_dashboard.html', page='dashboard',
                             companies=companies,
                             jobs=jobs_list,
                             my_company=my_company,
                             can_request_verification=can_request_verification,
                             verification_status=verification_status)


@bp.route('/pricing')
def pricing():
    plan_info = {}
    if 'user_id' in session:
        plan_info = auth_service.get_user_plan(session['user_id'])
    return render_template('index_pricing.html', page='pricing', plan_info=plan_info)


@bp.route('/about')
def about():
    return render_template('index_about.html', page='about')


@bp.route('/upgrade-plan/<plan>')
@login_required
def upgrade_plan(plan):
    if plan not in ['pro']:
        flash('باقة غير صالحة', 'error')
        return redirect(url_for('main.pricing'))

    try:
        company = company_service.get_company_by_employer(session['user_id'])
        if not company:
            flash('⚠️ يجب إنشاء شركة أولاً قبل الترقية', 'error')
            return redirect(url_for('companies.create'))

        user = User.query.get(session['user_id'])
        if user:
            user.plan = plan
            from datetime import datetime
            user.plan_month_start = datetime.now().date()
            user.payment_status = 'active'
            db.session.commit()

        company_service.upgrade_company_plan(company.id)
        flash('✅ تم الترقية وتوثيق الشركة بنجاح!', 'success')

    except Exception as e:
        flash('حدث خطأ أثناء الترقية', 'error')

    return redirect(url_for('main.dashboard'))


@bp.route('/confirm-payment/<plan>')
@login_required
def confirm_payment(plan):
    flash('🚧 نظام الدفع قيد التطوير. سيتم إطلاقه قريباً.', 'error')
    return redirect(url_for('main.pricing'))
