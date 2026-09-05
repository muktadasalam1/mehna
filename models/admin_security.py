import uuid
from extensions import db
from datetime import datetime, timezone


class AdminActivityLog(db.Model):
    __tablename__ = 'admin_activity_log'

    id = db.Column(db.Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    # FK to users.id is defined in migration SQL only (PostgreSQL uuid type
    # is incompatible with SQLAlchemy TEXT for FK constraints at create_all time).
    admin_id = db.Column(db.Text, nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    target_type = db.Column(db.String(50), nullable=True)
    target_id = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(500), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.Index('idx_activity_admin_created', 'admin_id', 'created_at'),
    )


class AdminSession(db.Model):
    __tablename__ = 'admin_sessions'

    id = db.Column(db.Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    # FK to users.id is defined in migration SQL only.
    admin_id = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    session_token = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_active_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.Index('idx_session_admin', 'admin_id'),
    )


# Action type constants
ACTION_USER_TOGGLED = 'user_toggled'
ACTION_USER_MADE_ADMIN = 'user_made_admin'
ACTION_USER_REMOVED_ADMIN = 'user_removed_admin'
ACTION_COMPANY_APPROVED = 'company_approved'
ACTION_COMPANY_REJECTED = 'company_rejected'
ACTION_COMPANY_DELETED = 'company_deleted'
ACTION_LOGIN = 'login'


def log_admin_activity(admin_id, action_type, target_type=None, target_id=None,
                       description=None, ip_address=None):
    """Log an admin activity. Call this at the point of success in admin routes."""
    try:
        log = AdminActivityLog(
            admin_id=admin_id,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            description=description,
            ip_address=ip_address,
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()
