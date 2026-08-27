import secrets
from datetime import datetime
from flask import session, request
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from config import Config


def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']


def generate_reset_token(email):
    from flask import current_app
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])


def verify_reset_token(token):
    from flask import current_app
    try:
        serializer = URLSafeTimedSerializer(current_app.secret_key)
        return serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=current_app.config['RESET_TOKEN_EXPIRY']
        )
    except:
        return None


login_attempts = {}
apply_attempts = {}


def check_rate_limit(key, max_attempts=None, window=None, attempt_type='login'):
    if max_attempts is None:
        if attempt_type == 'login':
            max_attempts = Config.RATE_LIMIT_LOGIN_MAX
            window = Config.RATE_LIMIT_LOGIN_WINDOW
        elif attempt_type == 'reset':
            max_attempts = Config.RATE_LIMIT_RESET_MAX
            window = Config.RATE_LIMIT_RESET_WINDOW
        elif attempt_type == 'apply':
            max_attempts = Config.RATE_LIMIT_APPLY_MAX
            window = Config.RATE_LIMIT_APPLY_WINDOW

    attempts_dict = login_attempts if attempt_type != 'apply' else apply_attempts

    now = datetime.now()
    if key in attempts_dict:
        attempts = [t for t in attempts_dict[key] if (now - t).seconds < window]
        attempts_dict[key] = attempts
        if len(attempts) >= max_attempts:
            return False
    else:
        attempts_dict[key] = []
    attempts_dict[key].append(now)
    return True


def add_security_headers(response):
    response.headers.update({
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.socket.io https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data: https:; connect-src 'self' ws: wss:;",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    })
    return response


def send_reset_email(to_email, reset_url):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from flask import current_app

    subject = "مهنة - استعادة كلمة المرور"
    body = f"""<div dir="rtl"><h2>استعادة كلمة المرور</h2><a href="{reset_url}">إعادة تعيين</a></div>"""

    if not current_app.config['MAIL_USERNAME']:
        print(f"\n{reset_url}\n")
        return True

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = current_app.config['MAIL_SENDER']
        msg['To'] = to_email
        msg.attach(MIMEText(body, 'html', 'utf-8'))

        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as s:
            s.starttls()
            s.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            s.send_message(msg)
        return True
    except Exception as e:
        print(f"خطأ: {e}")
        return False
