"""
Utility functions for security, tokens, and logging.
"""
import secrets
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, abort
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import pyotp
from cryptography.fernet import Fernet
import base64
from app.extensions import db
from app.models import AuditLog

# Configure logging
logger = logging.getLogger(__name__)


def get_serializer():
    """Get URL-safe timed serializer for tokens"""
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def generate_token(data, salt='default'):
    """Generate a secure, time-limited token"""
    serializer = get_serializer()
    return serializer.dumps(data, salt=salt)


def verify_token(token, salt='default', max_age=3600):
    """
    Verify a token and return the data.
    Returns None if token is invalid or expired.
    """
    serializer = get_serializer()
    try:
        data = serializer.loads(token, salt=salt, max_age=max_age)
        return data
    except (SignatureExpired, BadSignature) as e:
        logger.warning(f"Token verification failed: {str(e)}")
        return None


def generate_verification_token(user_id):
    """Generate email verification token"""
    return generate_token({'user_id': user_id}, salt='email-verification')


def verify_verification_token(token, max_age=3600):
    """Verify email verification token"""
    data = verify_token(token, salt='email-verification', max_age=max_age)
    return data['user_id'] if data else None


def generate_password_reset_token(user_id):
    """Generate password reset token"""
    return generate_token({'user_id': user_id}, salt='password-reset')


def verify_password_reset_token(token, max_age=3600):
    """Verify password reset token"""
    data = verify_token(token, salt='password-reset', max_age=max_age)
    return data['user_id'] if data else None


def get_fernet_key():
    """
    Get Fernet encryption key for TOTP secrets.
    In production, load from environment variable.
    """
    key = current_app.config.get('TOTP_ENCRYPTION_KEY')
    if not key:
        # Generate a key for development (NOT for production)
        key = Fernet.generate_key().decode()
        logger.warning("Using generated TOTP encryption key. Set TOTP_ENCRYPTION_KEY in production!")
    
    # Ensure key is properly formatted
    if isinstance(key, str):
        key = key.encode()
    
    # Pad or truncate to 32 bytes, then base64 encode
    key = key[:32].ljust(32, b'0')
    key = base64.urlsafe_b64encode(key)
    
    return key


def encrypt_totp_secret(secret):
    """Encrypt TOTP secret for storage"""
    try:
        fernet = Fernet(get_fernet_key())
        encrypted = fernet.encrypt(secret.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error(f"Failed to encrypt TOTP secret: {str(e)}")
        raise


def decrypt_totp_secret(encrypted_secret):
    """Decrypt TOTP secret from storage"""
    try:
        fernet = Fernet(get_fernet_key())
        decrypted = fernet.decrypt(encrypted_secret.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Failed to decrypt TOTP secret: {str(e)}")
        raise


def generate_totp_secret():
    """Generate a new TOTP secret"""
    return pyotp.random_base32()


def get_totp_uri(secret, email, issuer='DemandForecasting'):
    """Generate TOTP URI for QR code"""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def verify_totp_code(secret, code):
    """Verify TOTP code"""
    totp = pyotp.TOTP(secret)
    # Allow 1 time step before and after for clock skew
    return totp.verify(code, valid_window=1)


def log_audit_event(event_type, user_id=None, details=None):
    """
    Log security audit event.
    
    Args:
        event_type: Type of event (login_success, login_failed, etc.)
        user_id: User ID (optional)
        details: Additional details (optional)
    """
    try:
        audit_log = AuditLog(
            user_id=user_id,
            event_type=event_type,
            ip_address=request.remote_addr if request else None,
            user_agent=request.user_agent.string if request and request.user_agent else None,
            details=details
        )
        db.session.add(audit_log)
        db.session.commit()
        
        # Also log to file
        logger.info(f"AUDIT: {event_type} | User: {user_id} | IP: {request.remote_addr if request else 'N/A'} | Details: {details}")
    except Exception as e:
        logger.error(f"Failed to log audit event: {str(e)}")
        db.session.rollback()


def role_required(role):
    """
    Decorator to require specific role for route access.
    
    Usage:
        @role_required('admin')
        def admin_only_view():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_role(role):
                log_audit_event('unauthorized_access_attempt', 
                              user_id=current_user.id,
                              details=f"Attempted to access {role}-only resource")
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """
    Decorator to require admin role.
    
    Usage:
        @admin_required
        def admin_view():
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_admin():
            log_audit_event('unauthorized_access_attempt',
                          user_id=current_user.id,
                          details="Attempted to access admin resource")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def get_client_ip():
    """Get client IP address, considering proxies"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr


def is_safe_url(target):
    """Check if redirect URL is safe (same domain)"""
    from urllib.parse import urlparse, urljoin
    from flask import request
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def validate_password_strength(password):
    """
    Validate password strength.
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    
    if not (has_upper and has_lower and has_digit and has_special):
        return False, "Password must contain uppercase, lowercase, digit, and special character"
    
    return True, None


def sanitize_input(text, max_length=1000):
    """Basic input sanitization"""
    if not text:
        return text
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Limit length
    text = text[:max_length]
    
    return text.strip()


def setup_logging(app):
    """Configure application logging"""
    import os
    from logging.handlers import RotatingFileHandler
    
    # Create logs directory
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    
    # Add handlers
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')
