"""
Email sending functionality for authentication.
"""
from flask import current_app, render_template, url_for
from flask_mail import Message
from app.extensions import mail
import logging

logger = logging.getLogger(__name__)


def send_email(to, subject, template, **kwargs):
    """
    Send email with both HTML and plain text versions.
    
    Args:
        to: Recipient email address
        subject: Email subject
        template: Template name (without extension)
        **kwargs: Template variables
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[to],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@demandforecasting.com')
        )
        
        # Render both HTML and plain text versions
        msg.body = render_template(f'email/{template}.txt', **kwargs)
        msg.html = render_template(f'email/{template}.html', **kwargs)
        
        mail.send(msg)
        logger.info(f"Email sent to {to}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {str(e)}")
        return False


def send_verification_email(user, token):
    """Send email verification link"""
    verification_url = url_for('auth.verify_email', token=token, _external=True)
    
    return send_email(
        to=user.email,
        subject='Verify Your Email - Demand Forecasting',
        template='verify_email',
        user=user,
        verification_url=verification_url
    )


def send_password_reset_email(user, token):
    """Send password reset link"""
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    return send_email(
        to=user.email,
        subject='Password Reset Request - Demand Forecasting',
        template='reset_password',
        user=user,
        reset_url=reset_url
    )


def send_password_changed_email(user):
    """Notify user that password was changed"""
    return send_email(
        to=user.email,
        subject='Password Changed - Demand Forecasting',
        template='password_changed',
        user=user
    )


def send_account_locked_email(user):
    """Notify user that account was locked"""
    return send_email(
        to=user.email,
        subject='Account Locked - Demand Forecasting',
        template='account_locked',
        user=user
    )


def send_2fa_enabled_email(user):
    """Notify user that 2FA was enabled"""
    return send_email(
        to=user.email,
        subject='Two-Factor Authentication Enabled - Demand Forecasting',
        template='2fa_enabled',
        user=user
    )


def send_2fa_disabled_email(user):
    """Notify user that 2FA was disabled"""
    return send_email(
        to=user.email,
        subject='Two-Factor Authentication Disabled - Demand Forecasting',
        template='2fa_disabled',
        user=user
    )


def send_welcome_email(user):
    """Send welcome email after successful registration"""
    return send_email(
        to=user.email,
        subject='Welcome to Demand Forecasting',
        template='welcome',
        user=user
    )
