from datetime import datetime
from extensions import db
from models.application import Application
from models.job import Job
from models.user import User
from models.profile import Profile
from services.auth_service import get_user_plan, get_plan_limits
from services.notification_service import notify_application_status_changed, notify_employer_new_applicant


def has_applied(job_id, user_id):
    return Application.query.filter_by(job_id=job_id, job_seeker_id=user_id).first() is not None


def submit_application(job_id, user_id):
    if has_applied(job_id, user_id):
        return False, 'قدمت مسبقا'

    job = Job.query.get(job_id)
    if not job or not job.is_active:
        return False, 'الوظيفة غير موجودة'

    application = Application(
        job_id=job_id,
        job_seeker_id=user_id
    )
    db.session.add(application)
    db.session.commit()

    notify_employer_new_applicant(job.employer_id, job.title, job_id)

    return True, 'تم التقديم'


def is_app_owner(user_id, app_id):
    return db.session.query(Application).join(
        Job, Application.job_id == Job.id
    ).filter(
        Application.id == app_id,
        Job.employer_id == user_id
    ).first() is not None


def get_applicants_for_job(job_id, employer_id):
    job = Job.query.filter_by(id=job_id, employer_id=employer_id).first()
    if not job:
        return None, None

    applicants = db.session.query(
        Application,
        User.full_name,
        User.email,
        Profile.skills,
        Profile.phone
    ).join(
        User, Application.job_seeker_id == User.id
    ).outerjoin(
        Profile, User.id == Profile.user_id
    ).filter(
        Application.job_id == job_id
    ).order_by(
        Application.created_at.desc()
    ).all()

    return applicants, job


def manage_application(app_id, action, reviewer_id):
    if action not in ('accepted', 'rejected'):
        return False

    application = Application.query.get(app_id)
    if not application:
        return False

    job = Job.query.get(application.job_id)
    if not job or job.employer_id != reviewer_id:
        return False

    application.status = action
    application.reviewed_by = reviewer_id
    application.reviewed_at = datetime.utcnow()
    db.session.commit()

    msg = f'تم قبولك في "{job.title}"' if action == 'accepted' else f'تم رفضك في "{job.title}"'
    notify_application_status_changed(application.job_seeker_id, msg, action)

    return True


def get_seeker_applications(user_id):
    return db.session.query(
        Application,
        Job.title.label('job_title'),
        Job.company_id
    ).join(
        Job, Application.job_id == Job.id
    ).filter(
        Application.job_seeker_id == user_id
    ).order_by(
        Application.created_at.desc()
    ).all()


def get_pending_applications_count(employer_id):
    from sqlalchemy import func
    return db.session.query(func.count(Application.id)).join(
        Job, Application.job_id == Job.id
    ).filter(
        Job.employer_id == employer_id,
        Application.status == 'pending'
    ).scalar()
