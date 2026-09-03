import uuid
from extensions import db
from datetime import datetime, timezone


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = db.Column(db.String(36), db.ForeignKey('jobs.id'), nullable=False)
    job_seeker_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    cover_letter = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')
    notes = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_applications')

    __table_args__ = (
        db.UniqueConstraint('job_id', 'job_seeker_id', name='unique_application'),
    )
