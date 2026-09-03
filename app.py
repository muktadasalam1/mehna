import os
import logging
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template, request
from extensions import db, socketio, csrf, migrate
from config import Config
from utils.security import add_security_headers, generate_csrf_token


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins=app.config['WEBSOCKET_CORS_ORIGINS'].split(','),
                      ping_timeout=60, ping_interval=25,
                      max_http_buffer_size=100000, async_mode='threading',
                      logger=False, engineio_logger=False)
    csrf.init_app(app)

    _setup_logging(app)
    app.jinja_env.globals['csrf_token'] = generate_csrf_token

    @app.after_request
    def after_request(response):
        return add_security_headers(response)

    _register_error_handlers(app)
    _register_health_check(app)
    _register_blueprints(app)

    with app.app_context():
        from models import (User, Profile, Company, Job, Application,
                            Notification, SavedJob, Skill,
                            AdminActivityLog, AdminSession)
        db.create_all()
        _run_migrations()
        seed_data()

    return app


def _setup_logging(app):
    log_level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    app.logger.setLevel(log_level)


def _register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        if request_wants_json():
            return jsonify({'status': 'error', 'message': 'الصفحة غير موجودة'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        app.logger.error(f'Internal server error: {e}')
        if request_wants_json():
            return jsonify({'status': 'error', 'message': 'خطأ في الخادم'}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(e):
        if request_wants_json():
            return jsonify({'status': 'error', 'message': 'غير مصرح'}), 403
        return render_template('errors/403.html'), 403


def request_wants_json():
    from flask import request
    return request.path.startswith('/api/')


def _register_health_check(app):
    @app.route('/health')
    def health_check():
        try:
            db.session.execute(db.text('SELECT 1'))
            db_status = 'healthy'
        except Exception:
            db_status = 'unhealthy'

        status_code = 200 if db_status == 'healthy' else 503
        return jsonify({
            'status': 'healthy' if db_status == 'healthy' else 'degraded',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'services': {
                'database': db_status,
            }
        }), status_code


def _register_blueprints(app):
    from routes.auth import bp as auth_bp
    from routes.jobs import bp as jobs_bp
    from routes.companies import bp as companies_bp
    from routes.admin import bp as admin_bp
    from routes.notifications import bp as notifications_bp
    from routes.main import bp as main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(main_bp)


def _run_migrations():
    """Run lightweight migrations for columns that may not exist yet."""
    migrations = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_ip VARCHAR(45)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN DEFAULT FALSE",
    ]
    for sql in migrations:
        try:
            db.session.execute(db.text(sql))
        except Exception:
            pass
    db.session.commit()


def seed_data():
    from werkzeug.security import generate_password_hash
    from models.user import User
    from models.profile import Profile
    from models.company import Company
    from models.job import Job

    if User.query.filter_by(user_type='employer').count() > 0:
        return

    employer = User(
        email='employer@mehna.com',
        password_hash=generate_password_hash('123456'),
        full_name='أحمد محمد',
        user_type='employer',
        is_admin=True
    )
    db.session.add(employer)
    db.session.flush()

    company = Company(
        name='شركة التقنية',
        description='شركة تطوير',
        location='بغداد',
        industry='تقنية',
        size='11-50',
        is_verified=True,
        verification_status='verified'
    )
    db.session.add(company)
    db.session.flush()

    seeker = User(
        email='seeker@mehna.com',
        password_hash=generate_password_hash('123456'),
        full_name='علي حسين',
        user_type='job_seeker'
    )
    db.session.add(seeker)
    db.session.flush()

    profile = Profile(
        user_id=seeker.id,
        phone='07701234567',
        location='بغداد',
        bio='مطور',
        skills=['Python', 'Flask']
    )
    db.session.add(profile)

    jobs_data = [
        {
            'employer_id': employer.id,
            'company_id': company.id,
            'title': 'مطور Full Stack',
            'description': 'نبحث عن مطور',
            'salary_range': '1500-2500',
            'location': 'بغداد',
            'job_type': 'full_time'
        },
        {
            'employer_id': employer.id,
            'company_id': company.id,
            'title': 'مصمم UI/UX',
            'description': 'مطلوب مصمم',
            'salary_range': '1200-1800',
            'location': 'بغداد',
            'job_type': 'full_time'
        }
    ]

    for job_data in jobs_data:
        job = Job(**job_data)
        db.session.add(job)

    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    port = int(os.environ.get('PORT', 5000))
    app.logger.info(f"Server starting on http://0.0.0.0:{port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)
