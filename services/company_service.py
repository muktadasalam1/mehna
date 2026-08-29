from datetime import datetime
from extensions import db
from models.company import Company
from models.job import Job
from models.user import User


def get_company_by_employer(employer_id):
    return Company.query.filter(
        Company.jobs.any(employer_id=employer_id)
    ).first()


def get_companies_by_employer(employer_id):
    return Company.query.filter(
        Company.jobs.any(employer_id=employer_id)
    ).all()


def create_company(employer_id, name, description, website, location, owner_name, owner_id_number):
    existing = Company.query.filter_by(name=name).first()
    if existing:
        return None, '⚠️ اسم الشركة مستخدم مسبقاً، اختر اسماً آخر'

    docs = f"المالك: {owner_name}\nرقم الهوية: {owner_id_number}"
    company = Company(
        name=name,
        description=description,
        website=website,
        location=location,
        verification_status='pending',
        verification_documents=docs
    )
    db.session.add(company)
    db.session.commit()

    return company, '✅ تم تقديم الطلب بنجاح!'


def update_company(company_id, name, description, website, location):
    company = Company.query.get(company_id)
    if company:
        company.name = name
        company.description = description
        company.website = website
        company.location = location
        db.session.commit()
        return True
    return False


def delete_company(company_id, employer_id):
    company = Company.query.filter(
        Company.id == company_id,
        Company.jobs.any(employer_id=employer_id)
    ).first()

    if company:
        Job.query.filter_by(company_id=company_id).delete()
        db.session.delete(company)
        db.session.commit()
        return True
    return False


def is_company_owner(user_id, company_id):
    return Company.query.filter(
        Company.id == company_id,
        Company.jobs.any(employer_id=user_id)
    ).first() is not None


def request_verification(employer_id):
    company = get_company_by_employer(employer_id)
    if not company:
        return False, '⚠️ يجب إنشاء شركة أولاً'

    if company.verification_status == 'verified':
        return False, '✅ شركتك موثقة بالفعل!'

    if company.verification_status == 'pending':
        return False, '⏳ طلب التوثيق قيد المراجعة بالفعل'

    company.verification_status = 'pending'
    db.session.commit()
    return True, '✅ تم تقديم طلب التوثيق بنجاح! سيتم مراجعته من قبل الإدارة.'


def verify_company(company_id):
    company = Company.query.get(company_id)
    if company:
        company.verification_status = 'verified'
        company.verified_at = datetime.utcnow()
        company.is_verified = True
        db.session.commit()
        return True
    return False


def reject_company(company_id):
    company = Company.query.get(company_id)
    if company:
        company.verification_status = 'rejected'
        db.session.commit()
        return True
    return False


def get_pending_companies():
    return Company.query.filter_by(verification_status='pending').order_by(Company.created_at.desc()).all()


def get_verified_companies():
    return Company.query.filter_by(verification_status='verified').order_by(Company.created_at.desc()).limit(20).all()


def get_rejected_companies():
    return Company.query.filter_by(verification_status='rejected').order_by(Company.created_at.desc()).limit(10).all()


def get_all_companies():
    return Company.query.order_by(Company.created_at.desc()).all()


def get_company_stats(company_id):
    from sqlalchemy import func
    company = Company.query.get(company_id)
    if not company:
        return None

    jobs_count = Job.query.filter_by(company_id=company_id).count()
    applications_count = db.session.query(func.count(Application.id)).join(
        Job, Application.job_id == Job.id
    ).filter(Job.company_id == company_id).scalar()

    return {
        'company': company,
        'jobs_count': jobs_count,
        'applications_count': applications_count
    }


def upgrade_company_plan(company_id):
    company = Company.query.get(company_id)
    if company:
        company.verification_status = 'verified'
        company.verified_at = datetime.utcnow()
        db.session.commit()
        return True
    return False
