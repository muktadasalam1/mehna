from datetime import datetime
from extensions import db
from models.job import Job
from models.company import Company
from services.auth_service import check_job_limit


def get_active_jobs(limit=None):
    from sqlalchemy import func
    query = db.session.query(
        Job,
        Company.name.label('company_name')
    ).join(
        Company, Job.company_id == Company.id
    ).filter(
        Job.is_active == True
    ).order_by(
        Job.created_at.desc()
    )
    if limit:
        query = query.limit(limit)
    return query.all()


def get_job_by_id(job_id):
    return Job.query.get(job_id)


def increment_job_views(job_id):
    job = Job.query.get(job_id)
    if job:
        job.views_count += 1
        db.session.commit()
    return job


def create_job(employer_id, company_id, title, description, salary_range, location, job_type):
    can_post, msg, company = can_user_post_job(employer_id)
    if not can_post:
        return False, msg, None

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

    from models.user import User
    user = User.query.get(employer_id)
    if user:
        user.jobs_posted_this_month = (user.jobs_posted_this_month or 0) + 1

    db.session.commit()
    return True, '', job


def delete_job(job_id, employer_id):
    job = Job.query.filter_by(id=job_id, employer_id=employer_id).first()
    if job:
        db.session.delete(job)
        db.session.commit()
        return True
    return False


def open_job(job_id, employer_id):
    job = Job.query.filter_by(id=job_id, employer_id=employer_id).first()
    if job:
        job.is_active = True
        db.session.commit()
        return True
    return False


def close_job(job_id, employer_id):
    job = Job.query.filter_by(id=job_id, employer_id=employer_id).first()
    if job:
        job.is_active = False
        db.session.commit()
        return True
    return False


def is_job_owner(user_id, job_id):
    return Job.query.filter_by(id=job_id, employer_id=user_id).first() is not None


def can_user_post_job(user_id):
    company = Company.query.filter(
        Company.jobs.any(employer_id=user_id)
    ).first()

    if not company:
        return False, 'لا يوجد شركة مسجلة', None

    if company.verification_status == 'verified':
        from services.auth_service import get_user_plan, get_plan_limits
        plan_info = get_user_plan(user_id)
        limits = get_plan_limits(plan_info['plan'])
        if plan_info['jobs_posted'] >= limits['max_jobs']:
            return False, f'لقد وصلت للحد الأقصى ({limits["max_jobs"]} وظائف) في الباقة {limits["name"]}. قم بالترقية.', company
        return True, '', company

    jobs_count = Job.query.filter_by(company_id=company.id).count()
    if jobs_count >= 1:
        return False, '⚠️ شركتك غير موثقة. لا يمكنك نشر أكثر من وظيفة واحدة. قم بطلب التوثيق.', company

    return True, '', company


def get_employer_jobs(employer_id):
    from sqlalchemy import func
    jobs = db.session.query(
        Job,
        Company.name.label('company_name'),
        func.count(Job.applications.property.mapper.class_.id).label('applicant_count')
    ).join(
        Company, Job.company_id == Company.id
    ).outerjoin(
        Job.applications
    ).filter(
        Job.employer_id == employer_id
    ).group_by(
        Job.id, Company.name
    ).order_by(
        Job.created_at.desc()
    ).all()
    return jobs


def get_job_with_company(job_id):
    from sqlalchemy import func
    result = db.session.query(
        Job,
        Company.name.label('company_name')
    ).join(
        Company, Job.company_id == Company.id
    ).filter(
        Job.id == job_id
    ).first()
    return result
