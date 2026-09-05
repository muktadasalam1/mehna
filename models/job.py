import uuid
from extensions import db
from datetime import datetime, timezone


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    salary_range = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    job_type = db.Column(db.String(50), nullable=True)
    requirements = db.Column(db.ARRAY(db.String), nullable=True)
    benefits = db.Column(db.ARRAY(db.String), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    views_count = db.Column(db.Integer, default=0)
    applications_count = db.Column(db.Integer, default=0)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    applications = db.relationship('Application', backref='job', lazy='dynamic')
