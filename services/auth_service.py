from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from extensions import db


def register(email, password, full_name, user_type='job_seeker'):
    existing = User.query.filter_by(email=email).first()
    if existing:
        return None

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        full_name=full_name,
        user_type=user_type
    )
    db.session.add(user)
    db.session.commit()
    return user


def login(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def update_last_login(user_id):
    from datetime import datetime, timezone
    user = User.query.get(user_id)
    if user:
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()


def reset_password(user_id, new_password):
    user = User.query.get(user_id)
    if user:
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
    return user


def get_user_plan(user_id):
    user = User.query.get(user_id)
    if user:
        from config import Config
        plan_info = Config.PLAN_LIMITS.get(user.plan, Config.PLAN_LIMITS['free'])
        return {
            'plan': user.plan,
            'jobs_posted': user.jobs_posted_this_month or 0,
            **plan_info
        }
    return {}
