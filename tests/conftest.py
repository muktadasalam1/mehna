import pytest
from app import create_app
from extensions import db as _db
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret'
    SECURITY_PASSWORD_SALT = 'test-salt'
    MAIL_USERNAME = None
    MAIL_PASSWORD = None


@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    with app.app_context():
        _db.session.begin_nested()
        yield _db.session
        _db.session.rollback()


@pytest.fixture
def seed_users(db_session):
    from werkzeug.security import generate_password_hash
    from models.user import User

    employer = User(
        email='employer@test.com',
        password_hash=generate_password_hash('Password1'),
        full_name='Test Employer',
        user_type='employer',
        is_admin=False
    )
    seeker = User(
        email='seeker@test.com',
        password_hash=generate_password_hash('Password1'),
        full_name='Test Seeker',
        user_type='job_seeker'
    )
    admin = User(
        email='admin@test.com',
        password_hash=generate_password_hash('Password1'),
        full_name='Test Admin',
        user_type='employer',
        is_admin=True
    )
    db_session.add_all([employer, seeker, admin])
    db_session.commit()
    return {'employer': employer, 'seeker': seeker, 'admin': admin}
