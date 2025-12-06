"""
WTForms for authentication with validation.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp
from app.models import User
from app.utils import validate_password_strength


class RegistrationForm(FlaskForm):
    """User registration form"""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address'),
        Length(max=120)
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, max=128, message='Password must be between 8 and 128 characters')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        """Check if email is already registered"""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered. Please use a different email or login.')
    
    def validate_password(self, field):
        """Validate password strength"""
        is_valid, error_msg = validate_password_strength(field.data)
        if not is_valid:
            raise ValidationError(error_msg)


class LoginForm(FlaskForm):
    """User login form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    remember_me = BooleanField('Remember Me')
    
    totp_code = StringField('2FA Code (if enabled)', validators=[
        Length(min=6, max=6, message='2FA code must be 6 digits')
    ])
    
    submit = SubmitField('Login')


class ForgotPasswordForm(FlaskForm):
    """Forgot password form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    
    submit = SubmitField('Send Reset Link')


class ResetPasswordForm(FlaskForm):
    """Reset password form"""
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, max=128, message='Password must be between 8 and 128 characters')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    submit = SubmitField('Reset Password')
    
    def validate_password(self, field):
        """Validate password strength"""
        is_valid, error_msg = validate_password_strength(field.data)
        if not is_valid:
            raise ValidationError(error_msg)


class ChangePasswordForm(FlaskForm):
    """Change password form for logged-in users"""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, max=128, message='Password must be between 8 and 128 characters')
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ])
    
    submit = SubmitField('Change Password')
    
    def validate_new_password(self, field):
        """Validate password strength"""
        is_valid, error_msg = validate_password_strength(field.data)
        if not is_valid:
            raise ValidationError(error_msg)


class Enable2FAForm(FlaskForm):
    """Enable 2FA form"""
    totp_code = StringField('Verification Code', validators=[
        DataRequired(message='Verification code is required'),
        Length(min=6, max=6, message='Code must be 6 digits'),
        Regexp(r'^\d{6}$', message='Code must contain only digits')
    ])
    
    submit = SubmitField('Enable 2FA')


class Disable2FAForm(FlaskForm):
    """Disable 2FA form"""
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    totp_code = StringField('Current 2FA Code', validators=[
        DataRequired(message='2FA code is required'),
        Length(min=6, max=6, message='Code must be 6 digits'),
        Regexp(r'^\d{6}$', message='Code must contain only digits')
    ])
    
    submit = SubmitField('Disable 2FA')


class Verify2FAForm(FlaskForm):
    """Verify 2FA code during login"""
    totp_code = StringField('2FA Code', validators=[
        DataRequired(message='2FA code is required'),
        Length(min=6, max=6, message='Code must be 6 digits'),
        Regexp(r'^\d{6}$', message='Code must contain only digits')
    ])
    
    submit = SubmitField('Verify')
