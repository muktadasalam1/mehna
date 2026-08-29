from extensions import db
from datetime import datetime


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    size = db.Column(db.String(50), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    verification_documents = db.Column(db.Text, nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    jobs = db.relationship('Job', backref='company', lazy='dynamic')
