from extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'employer' or 'job_seeker'
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    plan = db.Column(db.String(20), default='free')
    jobs_posted_this_month = db.Column(db.Integer, default=0)
    plan_month_start = db.Column(db.Date, nullable=True)
    payment_status = db.Column(db.String(20), default='none')
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship('Profile', backref='user', uselist=False)
    companies = db.relationship('Company', secondary='jobs', backref='employers', viewonly=True)
    jobs_posted = db.relationship('Job', backref='employer', lazy='dynamic')
    applications = db.relationship('Application', backref='job_seeker', lazy='dynamic', foreign_keys='Application.job_seeker_id')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
