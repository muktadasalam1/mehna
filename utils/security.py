from datetime import datetime
from flask import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash
from config import Config


def generate_csrf_token():
    from flask import session
    if '_csrf_token' not in session:
        session['_csrf_token'] = generate_password_hash(str(datetime.now()))[:32]
    return session['_csrf_token']


def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


def generate_reset_token(user_id):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user_id, salt=current_app.config['SECURITY_PASSWORD_SALT'])


def verify_reset_token(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=current_app.config['RESET_TOKEN_EXPIRY']
        )
    except Exception:
        return None


login_attempts = {}
apply_attempts = {}
register_attempts = {}


def check_rate_limit(key, max_attempts=None, window=None, attempt_type='login'):
    from flask import current_app
    if attempt_type == 'login':
        max_attempts = max_attempts or Config.RATE_LIMIT_LOGIN_MAX
        window = window or Config.RATE_LIMIT_LOGIN_WINDOW
    elif attempt_type == 'reset':
        max_attempts = max_attempts or Config.RATE_LIMIT_RESET_MAX
        window = window or Config.RATE_LIMIT_RESET_WINDOW
    elif attempt_type == 'register':
        max_attempts = max_attempts or Config.RATE_LIMIT_REGISTER_MAX
        window = window or Config.RATE_LIMIT_REGISTER_WINDOW
    else:
        max_attempts = max_attempts or Config.RATE_LIMIT_APPLY_MAX
        window = window or Config.RATE_LIMIT_APPLY_WINDOW

    attempts_dict = {
        'login': login_attempts,
        'apply': apply_attempts,
        'register': register_attempts,
    }.get(attempt_type, login_attempts)

    now = datetime.now()
    if key in attempts_dict:
        attempts, timestamps = attempts_dict[key]
        timestamps = [t for t in timestamps if (now - t).total_seconds() < window]
        if len(timestamps) >= max_attempts:
            return False
        attempts_dict[key] = (attempts, timestamps)
    else:
        attempts_dict[key] = (0, [])

    attempts, timestamps = attempts_dict[key]
    attempts_dict[key] = (attempts + 1, timestamps + [now])
    return True


def send_reset_email(email, token):
    pass
