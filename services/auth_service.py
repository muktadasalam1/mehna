from datetime import datetime
from extensions import db
from models.user import User
from models.profile import Profile
from config import Config


def get_user_plan(user_id):
    user = User.query.get(user_id)
    if user:
        if user.plan_month_start and user.plan_month_start.month != datetime.now().month:
            user.jobs_posted_this_month = 0
            user.plan_month_start = datetime.now().date()
            db.session.commit()
            return {'plan': user.plan, 'jobs_posted': 0, 'payment_status': user.payment_status}
        return {'plan': user.plan, 'jobs_posted': user.jobs_posted_this_month or 0, 'payment_status': user.payment_status}
    return {'plan': 'free', 'jobs_posted': 0, 'payment_status': 'none'}


def get_plan_limits(plan):
    return Config.PLAN_LIMITS.get(plan, Config.PLAN_LIMITS['free'])


def check_job_limit(user_id):
    plan_info = get_user_plan(user_id)
    limits = get_plan_limits(plan_info['plan'])
    if plan_info['jobs_posted'] >= limits['max_jobs']:
        return False, limits, plan_info
    return True, limits, plan_info


def register_user(email, password, full_name, role):
    from werkzeug.security import generate_password_hash
    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        full_name=full_name,
        user_type=role
    )
    db.session.add(user)
    db.session.flush()

    if role == 'job_seeker':
        profile = Profile(user_id=user.id)
        db.session.add(profile)

    db.session.commit()
    return user


def authenticate_user(email, password):
    from werkzeug.security import check_password_hash
    user = User.query.filter_by(email=email, is_active=True).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None


def get_user_by_email(email):
    return User.query.filter_by(email=email, is_active=True).first()


def update_user_password(email, new_password):
    from werkzeug.security import generate_password_hash
    user = User.query.filter_by(email=email, is_active=True).first()
    if user:
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True
    return False


def update_last_login(user_id):
    user = User.query.get(user_id)
    if user:
        user.last_login = datetime.utcnow()
        db.session.commit()
