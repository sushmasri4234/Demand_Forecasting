"""
Database models for authentication and user management.
"""
from datetime import datetime, timedelta
from flask_login import UserMixin
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import secrets
from app.extensions import db

# Argon2 password hasher with secure parameters
ph = PasswordHasher(
    time_cost=2,  # Number of iterations
    memory_cost=65536,  # 64 MB
    parallelism=4,  # Number of parallel threads
    hash_len=32,  # Length of hash in bytes
    salt_len=16,  # Length of salt in bytes
)


class User(UserMixin, db.Model):
    """User model with authentication and security features"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    
    # Account status
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_locked = db.Column(db.Boolean, default=False, nullable=False)
    
    # Role-based access control
    role = db.Column(db.String(20), default='user', nullable=False)  # user, admin
    
    # 2FA
    totp_secret = db.Column(db.String(255), nullable=True)  # Encrypted TOTP secret
    is_2fa_enabled = db.Column(db.Boolean, default=False, nullable=False)
    
    # Security tracking
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True)
    
    # Remember me token
    remember_token = db.Column(db.String(255), nullable=True, unique=True)
    remember_token_expiry = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash password using Argon2"""
        self.password_hash = ph.hash(password)
    
    def check_password(self, password):
        """Verify password using Argon2"""
        try:
            ph.verify(self.password_hash, password)
            # Rehash if parameters have changed
            if ph.check_needs_rehash(self.password_hash):
                self.password_hash = ph.hash(password)
                db.session.commit()
            return True
        except VerifyMismatchError:
            return False
    
    def is_account_locked(self):
        """Check if account is currently locked"""
        if self.is_locked and self.locked_until:
            if datetime.utcnow() < self.locked_until:
                return True
            else:
                # Unlock account if lockout period has expired
                self.is_locked = False
                self.locked_until = None
                self.failed_login_attempts = 0
                db.session.commit()
                return False
        return self.is_locked
    
    def increment_failed_login(self, max_attempts=5, lockout_duration=900):
        """Increment failed login attempts and lock if threshold exceeded"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            self.is_locked = True
            self.locked_until = datetime.utcnow() + timedelta(seconds=lockout_duration)
        db.session.commit()
    
    def reset_failed_login(self):
        """Reset failed login attempts on successful login"""
        self.failed_login_attempts = 0
        self.is_locked = False
        self.locked_until = None
        db.session.commit()
    
    def generate_remember_token(self, duration_days=30):
        """Generate secure remember me token"""
        self.remember_token = secrets.token_urlsafe(32)
        self.remember_token_expiry = datetime.utcnow() + timedelta(days=duration_days)
        db.session.commit()
        return self.remember_token
    
    def verify_remember_token(self, token):
        """Verify remember me token"""
        if not self.remember_token or not self.remember_token_expiry:
            return False
        if datetime.utcnow() > self.remember_token_expiry:
            return False
        return secrets.compare_digest(self.remember_token, token)
    
    def revoke_remember_token(self):
        """Revoke remember me token"""
        self.remember_token = None
        self.remember_token_expiry = None
        db.session.commit()
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.email}>'


class AuditLog(db.Model):
    """Audit log for security events"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)
    # Event types: login_success, login_failed, logout, register, 
    # email_verified, password_changed, password_reset_requested,
    # password_reset_completed, 2fa_enabled, 2fa_disabled, 
    # account_locked, account_unlocked, suspicious_activity
    
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f'<AuditLog {self.event_type} at {self.timestamp}>'


class PasswordResetToken(db.Model):
    """Temporary tokens for password reset"""
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship('User', backref='reset_tokens')
    
    def is_valid(self):
        """Check if token is valid and not expired"""
        return not self.is_used and datetime.utcnow() < self.expires_at
    
    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        db.session.commit()
    
    @staticmethod
    def cleanup_expired():
        """Remove expired tokens (call periodically)"""
        expired = PasswordResetToken.query.filter(
            PasswordResetToken.expires_at < datetime.utcnow()
        ).all()
        for token in expired:
            db.session.delete(token)
        db.session.commit()


class EmailVerificationToken(db.Model):
    """Temporary tokens for email verification"""
    __tablename__ = 'email_verification_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship('User', backref='verification_tokens')
    
    def is_valid(self):
        """Check if token is valid and not expired"""
        return not self.is_used and datetime.utcnow() < self.expires_at
    
    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        db.session.commit()
    
    @staticmethod
    def cleanup_expired():
        """Remove expired tokens (call periodically)"""
        expired = EmailVerificationToken.query.filter(
            EmailVerificationToken.expires_at < datetime.utcnow()
        ).all()
        for token in expired:
            db.session.delete(token)
        db.session.commit()
