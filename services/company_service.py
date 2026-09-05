from models.company import Company
from extensions import db


def get_companies_by_employer(employer_id):
    from models.job import Job
    company_ids = db.session.query(Job.company_id).filter_by(
        employer_id=employer_id
    ).distinct().all()
    ids = [cid[0] for cid in company_ids]
    return Company.query.filter(Company.id.in_(ids)).all() if ids else []


def get_company_by_employer(employer_id):
    from models.job import Job
    job = Job.query.filter_by(employer_id=employer_id).first()
    if job:
        return Company.query.get(job.company_id)
    return None


def create_company(name, description, location, industry, size):
    company = Company(
        name=name,
        description=description,
        location=location,
        industry=industry,
        size=size
    )
    db.session.add(company)
    db.session.commit()
    return company


def verify_company(company_id):
    from datetime import datetime, timezone
    company = Company.query.get(company_id)
    if company:
        company.is_verified = True
        company.verification_status = 'verified'
        company.verified_at = datetime.now(timezone.utc)
        db.session.commit()
    return company


def reject_company(company_id):
    company = Company.query.get(company_id)
    if company:
        company.verification_status = 'rejected'
        db.session.commit()
    return company


def request_verification(company_id):
    company = Company.query.get(company_id)
    if company:
        company.verification_status = 'pending'
        db.session.commit()
    return company


def upgrade_company_plan(company_id):
    company = Company.query.get(company_id)
    if company:
        company.is_verified = True
        db.session.commit()
    return company
