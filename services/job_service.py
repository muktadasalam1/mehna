from models.job import Job
from models.company import Company
from extensions import db


def get_active_jobs(limit=None, location=None, job_type=None):
    query = Job.query.filter_by(is_active=True)
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    if job_type:
        query = query.filter_by(job_type=job_type)
    query = query.order_by(Job.created_at.desc())
    total = query.count()
    if limit:
        jobs = query.limit(limit).all()
    else:
        jobs = query.all()
    return jobs, total, location, job_type


def get_job_by_id(job_id):
    return Job.query.get(job_id)


def create_job(employer_id, company_id, title, description, salary_range, location, job_type):
    job = Job(
        employer_id=employer_id,
        company_id=company_id,
        title=title,
        description=description,
        salary_range=salary_range,
        location=location,
        job_type=job_type
    )
    db.session.add(job)
    db.session.commit()
    return job


def update_job(job_id, **kwargs):
    job = Job.query.get(job_id)
    if job:
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)
        db.session.commit()
    return job


def delete_job(job_id):
    job = Job.query.get(job_id)
    if job:
        job.is_active = False
        db.session.commit()
    return job


def get_jobs_by_employer(employer_id):
    return Job.query.filter_by(employer_id=employer_id).order_by(Job.created_at.desc()).all()


def increment_views(job_id):
    job = Job.query.get(job_id)
    if job:
        job.views_count = (job.views_count or 0) + 1
        db.session.commit()
