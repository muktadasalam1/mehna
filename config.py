import os
import secrets
from datetime import timedelta


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', secrets.token_hex(16))

    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    RESET_TOKEN_EXPIRY = 3600

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:123@localhost:5432/mehna_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'muktadasalam1111@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'ingixipzmttzlfju')
    MAIL_SENDER = os.environ.get('MAIL_USERNAME', 'muktadasalam1111@gmail.com')

    RATE_LIMIT_LOGIN_MAX = 5
    RATE_LIMIT_LOGIN_WINDOW = 300
    RATE_LIMIT_RESET_MAX = 3
    RATE_LIMIT_RESET_WINDOW = 900
    RATE_LIMIT_APPLY_MAX = 10
    RATE_LIMIT_APPLY_WINDOW = 3600

    PLAN_LIMITS = {
        'free': {'max_jobs': 1, 'max_applications': 10, 'name': 'مجانية', 'price': 0},
        'pro': {'max_jobs': 10, 'max_applications': 100, 'name': 'برو', 'price': 25000},
    }
