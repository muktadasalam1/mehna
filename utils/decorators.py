from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('سجل دخول اولا', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            if session.get('user_role') != role:
                flash('غير مصرح', 'error')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('سجل دخول اولا', 'error')
            return redirect(url_for('auth.login'))
        from models.user import User
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('للأدمن فقط', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated
