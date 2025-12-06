"""
Flask extensions initialization.
All extensions are initialized here and imported by the app factory.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect

# Initialize extensions (without app context)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

# Rate limiter with Redis backend
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",  # Will be overridden by config
)

# Security headers via Talisman
# CSP policy to prevent XSS
csp = {
    'default-src': "'self'",
    'script-src': [
        "'self'",
        "'unsafe-inline'",  # Required for Bootstrap inline scripts
        "https://cdn.jsdelivr.net",
        "https://cdn.plot.ly",
        "https://www.google.com",  # reCAPTCHA
        "https://www.gstatic.com",  # reCAPTCHA
    ],
    'style-src': [
        "'self'",
        "'unsafe-inline'",  # Required for inline styles
        "https://cdn.jsdelivr.net",
    ],
    'img-src': [
        "'self'",
        "data:",  # For QR codes
        "https:",
    ],
    'font-src': [
        "'self'",
        "https://cdn.jsdelivr.net",
    ],
    'frame-src': [
        "https://www.google.com",  # reCAPTCHA
    ],
}

talisman = Talisman(
    content_security_policy=csp,
    content_security_policy_nonce_in=['script-src'],
    force_https=False,  # Will be overridden by config
)


def init_login_manager(app):
    """Configure Flask-Login"""
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
