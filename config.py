import os
from datetime import timedelta


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')

    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    RESET_TOKEN_EXPIRY = 3600

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SENDER = os.environ.get('MAIL_SENDER', os.environ.get('MAIL_USERNAME'))

    RATE_LIMIT_LOGIN_MAX = 5
    RATE_LIMIT_LOGIN_WINDOW = 300
    RATE_LIMIT_REGISTER_MAX = 3
    RATE_LIMIT_REGISTER_WINDOW = 3600
    RATE_LIMIT_RESET_MAX = 3
    RATE_LIMIT_RESET_WINDOW = 900
    RATE_LIMIT_APPLY_MAX = 10
    RATE_LIMIT_APPLY_WINDOW = 3600

    PLAN_LIMITS = {
        'free': {'max_jobs': 1, 'max_applications': 10, 'name': 'مجانية', 'price': 0},
        'pro': {'max_jobs': 10, 'max_applications': 100, 'name': 'برو', 'price': 25000},
    }

    WEBSOCKET_CORS_ORIGINS = os.environ.get('WEBSOCKET_CORS_ORIGINS', 'http://localhost:5000')
