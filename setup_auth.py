"""
Complete setup script for authentication system.
This script creates all necessary templates, directories, and configuration files.
"""
import os
import secrets

def create_directories():
    """Create all necessary directories"""
    dirs = [
        'app/templates/auth',
        'app/templates/email',
        'app/templates/main',
        'app/static/css',
        'app/static/js',
        'logs',
        'uploads',
        'models',
        'migrations',
        'tests'
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"[OK] Created directory: {dir_path}")

def generate_env_file():
    """Generate .env file with secure random keys"""
    if os.path.exists('.env'):
        print("[WARNING] .env file already exists, skipping...")
        return
    
    secret_key = secrets.token_hex(32)
    argon2_key = secrets.token_hex(32)
    totp_key = secrets.token_hex(32)
    
    env_content = f"""# Flask Configuration
SECRET_KEY={secret_key}
FLASK_APP=run.py
FLASK_ENV=development

# Database Configuration
DATABASE_URL=sqlite:///demand_forecasting.db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Email Configuration (Configure for your SMTP server)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@demandforecasting.com

# Security Configuration
ARGON2_SECRET_KEY={argon2_key}
TOTP_ENCRYPTION_KEY={totp_key}

# Session Configuration
SESSION_COOKIE_SECURE=False
PERMANENT_SESSION_LIFETIME=3600
REMEMBER_COOKIE_DURATION=2592000

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://
RATELIMIT_ENABLED=True

# Account Security
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=900
PASSWORD_RESET_TOKEN_EXPIRY=3600
EMAIL_VERIFICATION_TOKEN_EXPIRY=3600

# HTTPS & Security Headers
FORCE_HTTPS=False
HSTS_ENABLED=False
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("[OK] Generated .env file with secure random keys")
    print("[WARNING] Remember to configure email settings in .env!")

def create_minimal_templates():
    """Create minimal required templates"""
    
    # Main home template
    main_home = """{% extends "base.html" %}
{% block title %}Home - Demand Forecasting{% endblock %}
{% block content %}
<div class="row mt-5">
    <div class="col-md-8 offset-md-2 text-center">
        <h1 class="display-4">🛒 Retail Demand Forecasting</h1>
        <p class="lead mt-4">AI-powered weekly demand forecasting with secure authentication</p>
        <div class="row mt-5">
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">📤 Upload Data</h5>
                        <p class="card-text">Upload CSV files with demand data</p>
                        <a href="{{ url_for('main.upload') }}" class="btn btn-primary">Upload</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">🤖 Train Model</h5>
                        <p class="card-text">Train ML models for products</p>
                        <a href="{{ url_for('main.train_select') }}" class="btn btn-primary">Train</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">🔮 Predict</h5>
                        <p class="card-text">Generate demand forecasts</p>
                        <a href="{{ url_for('main.predict') }}" class="btn btn-primary">Predict</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">📊 Dashboard</h5>
                        <p class="card-text">Interactive visualizations</p>
                        <a href="{{ url_for('main.dashboard') }}" class="btn btn-primary">Dashboard</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
    
    # Email verification template (plain text)
    verify_email_txt = """Hello {{ user.full_name }},

Thank you for registering with Demand Forecasting!

Please verify your email address by clicking the link below:

{{ verification_url }}

This link will expire in 1 hour.

If you did not create an account, please ignore this email.

Best regards,
Demand Forecasting Team
"""
    
    # Email verification template (HTML)
    verify_email_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .button { display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Welcome to Demand Forecasting!</h2>
        <p>Hello {{ user.full_name }},</p>
        <p>Thank you for registering. Please verify your email address by clicking the button below:</p>
        <p><a href="{{ verification_url }}" class="button">Verify Email Address</a></p>
        <p>Or copy and paste this link into your browser:</p>
        <p>{{ verification_url }}</p>
        <p>This link will expire in 1 hour.</p>
        <p>If you did not create an account, please ignore this email.</p>
        <p>Best regards,<br>Demand Forecasting Team</p>
    </div>
</body>
</html>
"""
    
    templates = {
        'app/templates/main/home.html': main_home,
        'app/templates/email/verify_email.txt': verify_email_txt,
        'app/templates/email/verify_email.html': verify_email_html,
    }
    
    for path, content in templates.items():
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Created template: {path}")

def create_docker_files():
    """Create Docker configuration files"""
    
    dockerfile = """FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_auth.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_auth.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p uploads models logs

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]
"""
    
    docker_compose = """version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/demand_forecasting
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads
      - ./models:/app/models
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:14-alpine
    environment:
      - POSTGRES_DB=demand_forecasting
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile)
    print("[OK] Created Dockerfile")
    
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose)
    print("[OK] Created docker-compose.yml")

def main():
    """Main setup function"""
    print("=" * 60)
    print("Authentication System Setup")
    print("=" * 60)
    print()
    
    print("Step 1: Creating directories...")
    create_directories()
    print()
    
    print("Step 2: Generating .env file...")
    generate_env_file()
    print()
    
    print("Step 3: Creating minimal templates...")
    create_minimal_templates()
    print()
    
    print("Step 4: Creating Docker files...")
    create_docker_files()
    print()
    
    print("=" * 60)
    print("[SUCCESS] Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Configure email settings in .env file")
    print("2. Install dependencies: pip install -r requirements_auth.txt")
    print("3. Run template generator: python generate_templates.py")
    print("4. Initialize database: flask db init && flask db migrate && flask db upgrade")
    print("5. Run application: python run.py")
    print()
    print("Default admin account:")
    print("  Email: admin@demandforecasting.com")
    print("  Password: Admin@123456")
    print("  [WARNING] CHANGE THIS IMMEDIATELY!")
    print()
    print("For full documentation, see AUTH_README.md")

if __name__ == '__main__':
    main()
