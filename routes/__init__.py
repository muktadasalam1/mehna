from routes.auth import bp as auth_bp
from routes.jobs import bp as jobs_bp
from routes.companies import bp as companies_bp
from routes.admin import bp as admin_bp
from routes.notifications import bp as notifications_bp
from routes.main import bp as main_bp

__all__ = ['auth_bp', 'jobs_bp', 'companies_bp', 'admin_bp', 'notifications_bp', 'main_bp']
