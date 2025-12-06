# 🔐 Authentication System Documentation

## Overview

A production-ready authentication system has been integrated into the Demand Forecasting application with comprehensive security features.

## ✅ Implemented Features

### Core Authentication
- ✅ User Registration with email verification
- ✅ Email verification with time-limited tokens
- ✅ Secure login with Argon2 password hashing
- ✅ "Remember me" functionality with secure tokens
- ✅ Password reset via email
- ✅ Two-Factor Authentication (2FA) with TOTP
- ✅ Account lockout after failed attempts
- ✅ Session management and secure logout

### Security Features
- ✅ Argon2 password hashing (strongest available)
- ✅ Rate limiting on all auth endpoints
- ✅ CSRF protection on all forms
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ XSS protection (template escaping + CSP)
- ✅ Secure session cookies (HttpOnly, Secure, SameSite)
- ✅ Account lockout and progressive delays
- ✅ Audit logging for all security events
- ✅ Email notifications for security events

### Role-Based Access Control
- ✅ User and Admin roles
- ✅ @admin_required decorator
- ✅ @role_required decorator
- ✅ Admin panel for user management

### Additional Features
- ✅ Password strength validation
- ✅ Email enumeration protection
- ✅ Token expiration and rotation
- ✅ Encrypted TOTP secrets
- ✅ QR code generation for 2FA setup
- ✅ Comprehensive audit logging

## 📁 Project Structure

```
demand_forecasting/
├── app/
│   ├── __init__.py              # App factory
│   ├── models.py                # User, AuditLog, Token models
│   ├── extensions.py            # Flask extensions
│   ├── utils.py                 # Security utilities
│   ├── email.py                 # Email sending
│   ├── auth/                    # Authentication blueprint
│   │   ├── __init__.py
│   │   ├── routes.py            # Auth routes
│   │   └── forms.py             # WTForms
│   ├── main/                    # Main app blueprint
│   │   ├── __init__.py
│   │   └── routes.py            # Forecasting routes
│   ├── templates/
│   │   ├── auth/                # Auth templates
│   │   ├── email/               # Email templates
│   │   └── main/                # Main app templates
│   └── static/
│       ├── css/
│       └── js/
├── migrations/                  # Database migrations
├── tests/                       # Test files
├── logs/                        # Application logs
├── uploads/                     # Uploaded data
├── models/                      # Trained ML models
├── config.py                    # Configuration
├── run.py                       # Application entry point
├── requirements_auth.txt        # All dependencies
├── .env.example                 # Environment variables template
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose
└── README_AUTH.md               # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_auth.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Critical settings to change:**
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `ARGON2_SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `TOTP_ENCRYPTION_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `MAIL_USERNAME` and `MAIL_PASSWORD` - Your SMTP credentials

### 3. Initialize Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4. Run Application

```bash
python run.py
```

Access at: **http://localhost:5000**

## 📧 Email Configuration

### Gmail Setup (Development)

1. Enable 2-Step Verification in your Google Account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Configure in `.env`:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Production Email Services

- **SendGrid**: https://sendgrid.com
- **Mailgun**: https://www.mailgun.com
- **Amazon SES**: https://aws.amazon.com/ses/

## 🔐 Security Configuration

### Password Requirements

- Minimum 8 characters
- Maximum 128 characters
- Must contain:
  - Uppercase letter
  - Lowercase letter
  - Digit
  - Special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

### Account Lockout

- **Max attempts**: 5 (configurable)
- **Lockout duration**: 15 minutes (configurable)
- **Email notification**: Sent on lockout

### Session Security

- **Session lifetime**: 1 hour (configurable)
- **Remember me duration**: 30 days (configurable)
- **Cookies**: HttpOnly, Secure (in production), SameSite=Lax

### Rate Limiting

- **Registration**: 5 per hour per IP
- **Login**: 10 per minute per IP
- **Password reset**: 3 per hour per IP
- **2FA verification**: 10 per minute per IP

## 🔑 Default Admin Account

**Email**: admin@demandforecasting.com  
**Password**: Admin@123456

**⚠️ CHANGE THIS IMMEDIATELY IN PRODUCTION!**

## 📝 API Routes

### Authentication Routes

| Method | Route | Description | Rate Limit |
|--------|-------|-------------|------------|
| GET/POST | /auth/register | User registration | 5/hour |
| GET | /auth/verify-email | Email verification | - |
| GET/POST | /auth/login | User login | 10/min |
| GET/POST | /auth/verify-2fa | 2FA verification | 10/min |
| GET | /auth/logout | User logout | - |
| GET/POST | /auth/forgot-password | Request password reset | 3/hour |
| GET/POST | /auth/reset-password | Reset password | 5/hour |
| GET | /auth/account | User account page | - |
| GET/POST | /auth/account/change-password | Change password | - |
| GET/POST | /auth/2fa/setup | Setup 2FA | - |
| GET/POST | /auth/2fa/disable | Disable 2FA | - |
| GET | /auth/admin/users | Admin user list | - |
| POST | /auth/admin/users/<id>/unlock | Unlock user account | - |
| POST | /auth/admin/users/<id>/revoke-sessions | Revoke user sessions | - |

### Main Application Routes (Protected)

| Method | Route | Description |
|--------|-------|-------------|
| GET | / | Homepage (redirects to login if not authenticated) |
| GET/POST | /upload | Upload CSV data |
| GET | /train_select | Select product for training |
| POST | /train | Train model |
| GET | /models | List trained models |
| GET/POST | /predict | Generate predictions |
| GET | /dashboard | Interactive dashboard |

## 🛡️ Security Best Practices

### Development

1. Use `.env` file for secrets (never commit!)
2. Use SQLite for local database
3. Use local Redis or memory storage for rate limiting
4. HTTPS not required locally

### Production

1. **Use strong secrets**: Generate with `secrets.token_hex(32)`
2. **Enable HTTPS**: Set `FORCE_HTTPS=True` and `SESSION_COOKIE_SECURE=True`
3. **Use PostgreSQL**: Better performance and features
4. **Use Redis**: For sessions and rate limiting
5. **Enable HSTS**: Set `HSTS_ENABLED=True`
6. **Configure CSP**: Adjust Content Security Policy as needed
7. **Use environment variables**: Never hardcode secrets
8. **Enable monitoring**: Set up logging and alerts
9. **Regular backups**: Database and uploaded files
10. **Update dependencies**: Keep packages up to date

## 🧪 Testing

### Run Tests

```bash
pytest tests/ -v --cov=app
```

### Test Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

## 📊 Audit Logging

All security events are logged to:
- **Database**: `audit_logs` table
- **File**: `logs/app.log`

### Event Types

- `register` - User registration
- `email_verified` - Email verification completed
- `login_success` - Successful login
- `login_failed` - Failed login attempt
- `logout` - User logout
- `password_changed` - Password changed
- `password_reset_requested` - Password reset requested
- `password_reset_completed` - Password reset completed
- `2fa_enabled` - 2FA enabled
- `2fa_disabled` - 2FA disabled
- `account_locked` - Account locked
- `account_unlocked` - Account unlocked
- `unauthorized_access_attempt` - Unauthorized access attempt
- `data_uploaded` - Data uploaded
- `model_trained` - Model trained
- `prediction_generated` - Prediction generated

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t demand-forecasting-auth .
```

### Run with Docker Compose

```bash
docker-compose up -d
```

This starts:
- Flask application
- PostgreSQL database
- Redis cache

## 🔧 Troubleshooting

### Email Not Sending

1. Check SMTP credentials in `.env`
2. For Gmail, use App Password (not regular password)
3. Check firewall/network settings
4. Review logs: `logs/app.log`

### Database Errors

```bash
# Reset database
flask db downgrade
flask db upgrade
```

### Redis Connection Error

```bash
# Use memory storage for development
RATELIMIT_STORAGE_URL=memory://
```

### 2FA Not Working

1. Ensure time is synchronized on server
2. Check TOTP_ENCRYPTION_KEY is set
3. Try regenerating QR code

## 📚 Additional Resources

### Security Headers

- **X-Frame-Options**: DENY (clickjacking protection)
- **X-Content-Type-Options**: nosniff
- **X-XSS-Protection**: 1; mode=block
- **Strict-Transport-Security**: max-age=31536000 (HSTS)
- **Content-Security-Policy**: Configured in `extensions.py`

### Password Hashing

Using Argon2id with parameters:
- **Time cost**: 2 iterations
- **Memory cost**: 64 MB
- **Parallelism**: 4 threads
- **Hash length**: 32 bytes
- **Salt length**: 16 bytes

### Token Security

- **Email verification**: 1 hour expiry
- **Password reset**: 1 hour expiry
- **Remember me**: 30 days expiry
- **All tokens**: Cryptographically signed with `itsdangerous`

## 🤝 Contributing

1. Follow PEP 8 style guide
2. Add tests for new features
3. Update documentation
4. Security fixes take priority

## 📄 License

This authentication system is part of the Demand Forecasting application and follows the same license.

---

**Built with security in mind using Flask, Argon2, and industry best practices.**

For questions or issues, please refer to the main README.md or open an issue.
