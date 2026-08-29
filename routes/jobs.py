from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.validators import sanitize
from utils.decorators import login_required, role_required
from services import job_service, application_service

bp = Blueprint('jobs', __name__, url_prefix='/jobs')


@bp.route('/')
def browse():
    from models.job import Job
    from models.company import Company
    jobs = job_service.get_active_jobs()
    return render_template('index_jobs.html', page='jobs', jobs=jobs)


@bp.route('/<job_id>')
def detail(job_id):
    job = job_service.get_job_by_id(job_id)
    if not job:
        flash('غير موجودة', 'error')
        return redirect(url_for('jobs.browse'))

    job_service.increment_job_views(job_id)

    applied = False
    if 'user_id' in session:
        applied = application_service.has_applied(job_id, session['user_id'])

    return render_template('index_job.html', page='job', job=job, applied=applied)


@bp.route('/post', methods=['POST'])
@login_required
@role_required('employer')
def post():
    try:
        from utils.validators import sanitize
        title = sanitize(request.form.get('title', ''), 100)
        description = sanitize(request.form.get('description', ''), 2000)

        if not title or not description:
            flash('جميع الحقول مطلوبة', 'error')
            return redirect(url_for('main.dashboard'))

        from models.company import Company
        company = Company.query.filter(
            Company.jobs.any(employer_id=session['user_id'])
        ).first()

        if not company:
            flash('يجب إنشاء شركة أولاً', 'error')
            return redirect(url_for('main.dashboard'))

        success, msg, job = job_service.create_job(
            employer_id=session['user_id'],
            company_id=company.id,
            title=title,
            description=description,
            salary_range=sanitize(request.form.get('salary', ''), 50),
            location=sanitize(request.form.get('location', ''), 100),
            job_type=sanitize(request.form.get('job_type', ''), 30)
        )

        if success:
            flash('✅ تم نشر الوظيفة بنجاح!', 'success')
        else:
            flash(msg, 'error')
            return redirect(url_for('pricing'))

    except Exception as e:
        flash('حدث خطأ أثناء نشر الوظيفة', 'error')

    return redirect(url_for('main.dashboard'))


@bp.route('/<job_id>/<action>')
@login_required
@role_required('employer')
def action(job_id, action):
    if action not in ('delete', 'open', 'close'):
        return redirect(url_for('main.dashboard'))

    if not job_service.is_job_owner(session['user_id'], job_id):
        flash('غير مصرح', 'error')
        return redirect(url_for('main.dashboard'))

    if action == 'delete':
        job_service.delete_job(job_id, session['user_id'])
    elif action == 'open':
        job_service.open_job(job_id, session['user_id'])
    else:
        job_service.close_job(job_id, session['user_id'])

    flash('تم', 'success')
    return redirect(url_for('main.dashboard'))


@bp.route('/<job_id>/apply', methods=['POST'])
@login_required
@role_required('job_seeker')
def apply(job_id):
    from utils.security import check_rate_limit
    if not check_rate_limit(f"apply_{session['user_id']}", attempt_type='apply'):
        flash('تجاوزت الحد', 'error')
        return redirect(url_for('jobs.detail', job_id=job_id))

    success, msg = application_service.submit_application(job_id, session['user_id'])
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('main.dashboard'))


@bp.route('/<job_id>/applicants')
@login_required
@role_required('employer')
def applicants(job_id):
    if not job_service.is_job_owner(session['user_id'], job_id):
        flash('غير مصرح', 'error')
        return redirect(url_for('main.dashboard'))

    applicants_list, job = application_service.get_applicants_for_job(job_id, session['user_id'])
    return render_template('index_applicants.html', page='applicants', applicants=applicants_list, job=job)


@bp.route('/application/<app_id>/<action>', methods=['POST'])
@login_required
def manage_application(app_id, action):
    if action not in ('accepted', 'rejected'):
        flash('غير مصرح', 'error')
        return redirect(url_for('main.dashboard'))

    if not application_service.is_app_owner(session['user_id'], app_id):
        flash('غير مصرح', 'error')
        return redirect(url_for('main.dashboard'))

    application_service.manage_application(app_id, action, session['user_id'])
    flash('تم', 'success')
    return redirect(url_for('main.dashboard'))
