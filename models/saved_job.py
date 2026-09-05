import uuid
from extensions import db
from datetime import datetime, timezone


class SavedJob(db.Model):
    __tablename__ = 'saved_jobs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.String(36), db.ForeignKey('jobs.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='saved_jobs')
    job = db.relationship('Job', backref='saved_by')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'job_id', name='unique_saved_job'),
    )
