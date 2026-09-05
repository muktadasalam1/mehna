from models.application import Application
from models.job import Job
from extensions import db


def apply_to_job(job_seeker_id, job_id, cover_letter=None):
    existing = Application.query.filter_by(
        job_seeker_id=job_seeker_id, job_id=job_id
    ).first()
    if existing:
        return None

    application = Application(
        job_seeker_id=job_seeker_id,
        job_id=job_id,
        cover_letter=cover_letter
    )
    db.session.add(application)

    job = Job.query.get(job_id)
    if job:
        job.applications_count = (job.applications_count or 0) + 1

    db.session.commit()
    return application


def get_applications_by_job(job_id):
    return Application.query.filter_by(job_id=job_id).order_by(Application.created_at.desc()).all()


def get_applications_by_seeker(seeker_id):
    return Application.query.filter_by(job_seeker_id=seeker_id).order_by(Application.created_at.desc()).all()


def update_application_status(application_id, status, reviewed_by=None):
    application = Application.query.get(application_id)
    if application:
        application.status = status
        application.reviewed_by = reviewed_by
        from datetime import datetime, timezone
        application.reviewed_at = datetime.now(timezone.utc)
        db.session.commit()
    return application


def has_applied(seeker_id, job_id):
    return Application.query.filter_by(
        job_seeker_id=seeker_id, job_id=job_id
    ).first() is not None
