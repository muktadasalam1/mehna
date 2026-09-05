import uuid
from extensions import db
from datetime import datetime, timezone


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.ARRAY(db.String), nullable=True)
    years_experience = db.Column(db.Integer, nullable=True)
    education = db.Column(db.ARRAY(db.String), nullable=True)
    certifications = db.Column(db.ARRAY(db.String), nullable=True)
    github_url = db.Column(db.String(255), nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
