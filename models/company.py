import uuid
from extensions import db
from datetime import datetime, timezone


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    size = db.Column(db.String(50), nullable=True)
    logo_url = db.Column(db.String(500), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    verification_status = db.Column(db.String(20), default='pending')
    verification_documents = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    jobs = db.relationship('Job', backref='company', lazy='dynamic')
    verifier = db.relationship('User', foreign_keys=[verified_by], backref='verified_companies')
