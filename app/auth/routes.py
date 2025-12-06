"""
Authentication routes with security features.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, timedelta
import secrets
import io
import qrcode
import base64

from app.extensions import db, limiter
from app.models import User, AuditLog, PasswordResetToken, EmailVerificationToken
from app.auth.forms import (
    RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm,
    ChangePasswordForm, Enable2FAForm, Disable2FAForm, Verify2FAForm
)
from app.email import (
    send_verification_email, send_password_reset_email, send_password_changed_email,
    send_account_locked_email, send_2fa_enabled_email, send_2fa_disabled_email,
    send_welcome_email
)
from app.utils import (
    generate_verification_token, verify_verification_token,
    generate_password_reset_token, verify_password_reset_token,
    log_audit_event, get_client_ip, is_safe_url,
    generate_totp_secret, get_totp_uri, verify_totp_code,
    encrypt_totp_secret, decrypt_totp_secret, admin_required
)

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")  # Rate limit registration
def register():
    """User registration with email verification"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Create new user
            user = User(
                email=form.email.data.lower().strip(),
                full_name=form.full_name.data.strip(),
                is_active=False,  # Inactive until email verified
                is_verified=False
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            # Generate verification token
            token = generate_verification_token(user.id)
            
            # Create verification token record
            expiry = datetime.utcnow() + timedelta(
                seconds=current_app.config.get('EMAIL_VERIFICATION_TOKEN_EXPIRY', 3600)
            )
            verification_token = EmailVerificationToken(
                user_id=user.id,
                token=token,
                expires_at=expiry
            )
            db.session.add(verification_token)
            db.session.commit()
            
            # Send verification email
            send_verification_email(user, token)
            
            # Log audit event
            log_audit_event('register', user_id=user.id, 
                          details=f"New user registered: {user.email}")
            
            flash('Registration successful! Please check your email to verify your account.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)


@auth.route('/verify-email')
def verify_email():
    """Verify email address with token"""
    token = request.args.get('token')
    
    if not token:
        flash('Invalid verification link.', 'error')
        return redirect(url_for('auth.login'))
    
    # Verify token
    user_id = verify_verification_token(
        token,
        max_age=current_app.config.get('EMAIL_VERIFICATION_TOKEN_EXPIRY', 3600)
    )
    
    if not user_id:
        flash('Verification link is invalid or has expired.', 'error')
        return redirect(url_for('auth.login'))
    
    # Check token in database
    verification_token = EmailVerificationToken.query.filter_by(
        token=token, user_id=user_id
    ).first()
    
    if not verification_token or not verification_token.is_valid():
        flash('Verification link is invalid or has expired.', 'error')
        return redirect(url_for('auth.login'))
    
    # Activate user
    user = User.query.get(user_id)
    if user:
        user.is_verified = True
        user.is_active = True
        verification_token.mark_as_used()
        db.session.commit()
        
        # Send welcome email
        send_welcome_email(user)
        
        # Log audit event
        log_audit_event('email_verified', user_id=user.id)
        
        flash('Email verified successfully! You can now log in.', 'success')
    else:
        flash('User not found.', 'error')
    
    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Rate limit login attempts
def login():
    """User login with 2FA support"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        
        # Generic error message to avoid email enumeration
        error_msg = 'Invalid email or password.'
        
        if not user:
            log_audit_event('login_failed', details=f"Login attempt for non-existent email: {email}")
            flash(error_msg, 'error')
            return render_template('auth/login.html', form=form)
        
        # Check if account is locked
        if user.is_account_locked():
            log_audit_event('login_failed', user_id=user.id, 
                          details="Login attempt on locked account")
            send_account_locked_email(user)
            flash('Account is temporarily locked due to multiple failed login attempts. Please try again later.', 'error')
            return render_template('auth/login.html', form=form)
        
        # Check if account is verified
        if not user.is_verified:
            flash('Please verify your email address before logging in.', 'error')
            return render_template('auth/login.html', form=form)
        
        # Verify password
        if not user.check_password(form.password.data):
            user.increment_failed_login(
                max_attempts=current_app.config.get('MAX_LOGIN_ATTEMPTS', 5),
                lockout_duration=current_app.config.get('ACCOUNT_LOCKOUT_DURATION', 900)
            )
            log_audit_event('login_failed', user_id=user.id, 
                          details="Invalid password")
            flash(error_msg, 'error')
            return render_template('auth/login.html', form=form)
        
        # Check 2FA if enabled
        if user.is_2fa_enabled:
            totp_code = form.totp_code.data
            
            if not totp_code:
                # Store user ID in session for 2FA verification
                session['2fa_user_id'] = user.id
                session['2fa_remember'] = form.remember_me.data
                return redirect(url_for('auth.verify_2fa'))
            
            # Verify TOTP code
            try:
                decrypted_secret = decrypt_totp_secret(user.totp_secret)
                if not verify_totp_code(decrypted_secret, totp_code):
                    user.increment_failed_login(
                        max_attempts=current_app.config.get('MAX_LOGIN_ATTEMPTS', 5),
                        lockout_duration=current_app.config.get('ACCOUNT_LOCKOUT_DURATION', 900)
                    )
                    log_audit_event('login_failed', user_id=user.id, 
                                  details="Invalid 2FA code")
                    flash('Invalid 2FA code.', 'error')
                    return render_template('auth/login.html', form=form)
            except Exception as e:
                current_app.logger.error(f"2FA verification error: {str(e)}")
                flash('An error occurred during 2FA verification.', 'error')
                return render_template('auth/login.html', form=form)
        
        # Successful login
        user.reset_failed_login()
        user.last_login = datetime.utcnow()
        user.last_login_ip = get_client_ip()
        db.session.commit()
        
        # Log in user
        login_user(user, remember=form.remember_me.data)
        
        # Generate remember token if requested
        if form.remember_me.data:
            user.generate_remember_token(
                duration_days=current_app.config.get('REMEMBER_COOKIE_DURATION', 2592000) // 86400
            )
        
        # Log audit event
        log_audit_event('login_success', user_id=user.id)
        
        flash(f'Welcome back, {user.full_name}!', 'success')
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        if next_page and is_safe_url(next_page):
            return redirect(next_page)
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html', form=form)


@auth.route('/verify-2fa', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def verify_2fa():
    """Verify 2FA code during login"""
    user_id = session.get('2fa_user_id')
    
    if not user_id:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(user_id)
    if not user or not user.is_2fa_enabled:
        session.pop('2fa_user_id', None)
        return redirect(url_for('auth.login'))
    
    form = Verify2FAForm()
    
    if form.validate_on_submit():
        try:
            decrypted_secret = decrypt_totp_secret(user.totp_secret)
            
            if verify_totp_code(decrypted_secret, form.totp_code.data):
                # Successful 2FA verification
                user.reset_failed_login()
                user.last_login = datetime.utcnow()
                user.last_login_ip = get_client_ip()
                db.session.commit()
                
                # Log in user
                remember = session.get('2fa_remember', False)
                login_user(user, remember=remember)
                
                if remember:
                    user.generate_remember_token()
                
                # Clean up session
                session.pop('2fa_user_id', None)
                session.pop('2fa_remember', None)
                
                # Log audit event
                log_audit_event('login_success', user_id=user.id, details="2FA verified")
                
                flash(f'Welcome back, {user.full_name}!', 'success')
                
                next_page = request.args.get('next')
                if next_page and is_safe_url(next_page):
                    return redirect(next_page)
                return redirect(url_for('main.index'))
            else:
                user.increment_failed_login(
                    max_attempts=current_app.config.get('MAX_LOGIN_ATTEMPTS', 5),
                    lockout_duration=current_app.config.get('ACCOUNT_LOCKOUT_DURATION', 900)
                )
                log_audit_event('login_failed', user_id=user.id, details="Invalid 2FA code")
                flash('Invalid 2FA code. Please try again.', 'error')
        except Exception as e:
            current_app.logger.error(f"2FA verification error: {str(e)}")
            flash('An error occurred during verification.', 'error')
    
    return render_template('auth/verify_2fa.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """User logout"""
    user_id = current_user.id
    
    # Revoke remember token
    if current_user.remember_token:
        current_user.revoke_remember_token()
    
    # Log audit event
    log_audit_event('logout', user_id=user_id)
    
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("3 per hour")  # Rate limit password reset requests
def forgot_password():
    """Request password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        
        # Always show success message to avoid email enumeration
        flash('If an account exists with that email, you will receive password reset instructions.', 'info')
        
        if user and user.is_verified:
            # Generate reset token
            token = generate_password_reset_token(user.id)
            
            # Create reset token record
            expiry = datetime.utcnow() + timedelta(
                seconds=current_app.config.get('PASSWORD_RESET_TOKEN_EXPIRY', 3600)
            )
            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token,
                expires_at=expiry
            )
            db.session.add(reset_token)
            db.session.commit()
            
            # Send reset email
            send_password_reset_email(user, token)
            
            # Log audit event
            log_audit_event('password_reset_requested', user_id=user.id)
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)


@auth.route('/reset-password', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def reset_password():
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    token = request.args.get('token')
    
    if not token:
        flash('Invalid password reset link.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    # Verify token
    user_id = verify_password_reset_token(
        token,
        max_age=current_app.config.get('PASSWORD_RESET_TOKEN_EXPIRY', 3600)
    )
    
    if not user_id:
        flash('Password reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    # Check token in database
    reset_token = PasswordResetToken.query.filter_by(
        token=token, user_id=user_id
    ).first()
    
    if not reset_token or not reset_token.is_valid():
        flash('Password reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.get(user_id)
        
        if user:
            user.set_password(form.password.data)
            reset_token.mark_as_used()
            
            # Reset failed login attempts
            user.reset_failed_login()
            
            db.session.commit()
            
            # Send confirmation email
            send_password_changed_email(user)
            
            # Log audit event
            log_audit_event('password_reset_completed', user_id=user.id)
            
            flash('Password reset successful! You can now log in with your new password.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('User not found.', 'error')
            return redirect(url_for('auth.forgot_password'))
    
    return render_template('auth/reset_password.html', form=form, token=token)


@auth.route('/account')
@login_required
def account():
    """User account page"""
    return render_template('auth/account.html', user=current_user)


@auth.route('/account/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password for logged-in user"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('auth/change_password.html', form=form)
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        # Send confirmation email
        send_password_changed_email(current_user)
        
        # Log audit event
        log_audit_event('password_changed', user_id=current_user.id)
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.account'))
    
    return render_template('auth/change_password.html', form=form)


@auth.route('/2fa/setup', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    """Setup 2FA for user"""
    if current_user.is_2fa_enabled:
        flash('2FA is already enabled for your account.', 'info')
        return redirect(url_for('auth.account'))
    
    form = Enable2FAForm()
    
    # Generate new TOTP secret if not in session
    if '2fa_secret' not in session:
        session['2fa_secret'] = generate_totp_secret()
    
    secret = session['2fa_secret']
    
    if form.validate_on_submit():
        # Verify the code
        if verify_totp_code(secret, form.totp_code.data):
            # Encrypt and save secret
            try:
                encrypted_secret = encrypt_totp_secret(secret)
                current_user.totp_secret = encrypted_secret
                current_user.is_2fa_enabled = True
                db.session.commit()
                
                # Clean up session
                session.pop('2fa_secret', None)
                
                # Send confirmation email
                send_2fa_enabled_email(current_user)
                
                # Log audit event
                log_audit_event('2fa_enabled', user_id=current_user.id)
                
                flash('Two-factor authentication enabled successfully!', 'success')
                return redirect(url_for('auth.account'))
            except Exception as e:
                current_app.logger.error(f"Failed to enable 2FA: {str(e)}")
                flash('An error occurred while enabling 2FA. Please try again.', 'error')
        else:
            flash('Invalid verification code. Please try again.', 'error')
    
    # Generate QR code
    totp_uri = get_totp_uri(secret, current_user.email)
    qr = qrcode.make(totp_uri)
    
    # Convert QR code to base64 for display
    buffer = io.BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return render_template('auth/setup_2fa.html', form=form, 
                         qr_code=qr_base64, secret=secret)


@auth.route('/2fa/disable', methods=['GET', 'POST'])
@login_required
def disable_2fa():
    """Disable 2FA for user"""
    if not current_user.is_2fa_enabled:
        flash('2FA is not enabled for your account.', 'info')
        return redirect(url_for('auth.account'))
    
    form = Disable2FAForm()
    
    if form.validate_on_submit():
        # Verify password
        if not current_user.check_password(form.password.data):
            flash('Incorrect password.', 'error')
            return render_template('auth/disable_2fa.html', form=form)
        
        # Verify TOTP code
        try:
            decrypted_secret = decrypt_totp_secret(current_user.totp_secret)
            if not verify_totp_code(decrypted_secret, form.totp_code.data):
                flash('Invalid 2FA code.', 'error')
                return render_template('auth/disable_2fa.html', form=form)
        except Exception as e:
            current_app.logger.error(f"Failed to verify 2FA: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
            return render_template('auth/disable_2fa.html', form=form)
        
        # Disable 2FA
        current_user.totp_secret = None
        current_user.is_2fa_enabled = False
        db.session.commit()
        
        # Send confirmation email
        send_2fa_disabled_email(current_user)
        
        # Log audit event
        log_audit_event('2fa_disabled', user_id=current_user.id)
        
        flash('Two-factor authentication disabled successfully.', 'success')
        return redirect(url_for('auth.account'))
    
    return render_template('auth/disable_2fa.html', form=form)


@auth.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Admin page to view and manage users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('auth/admin_users.html', users=users)


@auth.route('/admin/users/<int:user_id>/unlock', methods=['POST'])
@login_required
@admin_required
def admin_unlock_user(user_id):
    """Admin endpoint to unlock user account"""
    user = User.query.get_or_404(user_id)
    
    user.is_locked = False
    user.locked_until = None
    user.failed_login_attempts = 0
    db.session.commit()
    
    # Log audit event
    log_audit_event('account_unlocked', user_id=user.id, 
                  details=f"Unlocked by admin {current_user.id}")
    
    flash(f'Account for {user.email} has been unlocked.', 'success')
    return redirect(url_for('auth.admin_users'))


@auth.route('/admin/users/<int:user_id>/revoke-sessions', methods=['POST'])
@login_required
@admin_required
def admin_revoke_sessions(user_id):
    """Admin endpoint to revoke all user sessions"""
    user = User.query.get_or_404(user_id)
    
    user.revoke_remember_token()
    db.session.commit()
    
    # Log audit event
    log_audit_event('sessions_revoked', user_id=user.id,
                  details=f"Sessions revoked by admin {current_user.id}")
    
    flash(f'All sessions for {user.email} have been revoked.', 'success')
    return redirect(url_for('auth.admin_users'))
