from extensions import db
from datetime import datetime


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    salary_range = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    job_type = db.Column(db.String(30), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    views_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='job', lazy='dynamic')
