"""
Script to generate all HTML templates for the authentication system.
Run this script to create all necessary template files.
"""
import os

# Create directories
os.makedirs('app/templates/auth', exist_ok=True)
os.makedirs('app/templates/email', exist_ok=True)
os.makedirs('app/templates/main', exist_ok=True)

# Base template
base_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Demand Forecasting{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding-top: 60px; }
        .navbar-brand { font-weight: bold; }
        .password-strength { height: 5px; margin-top: 5px; border-radius: 3px; }
        .strength-weak { background-color: #dc3545; }
        .strength-medium { background-color: #ffc107; }
        .strength-strong { background-color: #28a745; }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% if current_user.is_authenticated %}
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('main.index') }}">📊 Demand Forecasting</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('main.index') }}">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('main.upload') }}">Upload Data</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('main.train_select') }}">Train Model</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('main.models') }}">Models</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('main.predict') }}">Predict</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('main.dashboard') }}">Dashboard</a></li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                            {{ current_user.full_name }}
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('auth.account') }}">My Account</a></li>
                            {% if current_user.is_admin() %}
                            <li><a class="dropdown-item" href="{{ url_for('auth.admin_users') }}">Admin Panel</a></li>
                            {% endif %}
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('auth.logout') }}">Logout</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    {% endif %}

    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
"""

# Login template
login_html = """{% extends "base.html" %}
{% block title %}Login - Demand Forecasting{% endblock %}
{% block content %}
<div class="row mt-5">
    <div class="col-md-6 offset-md-3">
        <div class="card">
            <div class="card-body">
                <h2 class="card-title text-center mb-4">🔐 Login</h2>
                <form method="POST" novalidate>
                    {{ form.hidden_tag() }}
                    <div class="mb-3">
                        {{ form.email.label(class="form-label") }}
                        {{ form.email(class="form-control" + (" is-invalid" if form.email.errors else "")) }}
                        {% if form.email.errors %}
                            <div class="invalid-feedback">{{ form.email.errors[0] }}</div>
                        {% endif %}
                    </div>
                    <div class="mb-3">
                        {{ form.password.label(class="form-label") }}
                        {{ form.password(class="form-control" + (" is-invalid" if form.password.errors else "")) }}
                        {% if form.password.errors %}
                            <div class="invalid-feedback">{{ form.password.errors[0] }}</div>
                        {% endif %}
                    </div>
                    <div class="mb-3">
                        {{ form.totp_code.label(class="form-label") }}
                        {{ form.totp_code(class="form-control", placeholder="Leave blank if 2FA not enabled") }}
                    </div>
                    <div class="mb-3 form-check">
                        {{ form.remember_me(class="form-check-input") }}
                        {{ form.remember_me.label(class="form-check-label") }}
                    </div>
                    {{ form.submit(class="btn btn-primary w-100") }}
                </form>
                <hr>
                <div class="text-center">
                    <p><a href="{{ url_for('auth.forgot_password') }}">Forgot Password?</a></p>
                    <p>Don't have an account? <a href="{{ url_for('auth.register') }}">Register here</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# Register template
register_html = """{% extends "base.html" %}
{% block title %}Register - Demand Forecasting{% endblock %}
{% block content %}
<div class="row mt-5">
    <div class="col-md-6 offset-md-3">
        <div class="card">
            <div class="card-body">
                <h2 class="card-title text-center mb-4">📝 Register</h2>
                <form method="POST" novalidate>
                    {{ form.hidden_tag() }}
                    <div class="mb-3">
                        {{ form.full_name.label(class="form-label") }}
                        {{ form.full_name(class="form-control" + (" is-invalid" if form.full_name.errors else "")) }}
                        {% if form.full_name.errors %}
                            <div class="invalid-feedback">{{ form.full_name.errors[0] }}</div>
                        {% endif %}
                    </div>
                    <div class="mb-3">
                        {{ form.email.label(class="form-label") }}
                        {{ form.email(class="form-control" + (" is-invalid" if form.email.errors else "")) }}
                        {% if form.email.errors %}
                            <div class="invalid-feedback">{{ form.email.errors[0] }}</div>
                        {% endif %}
                    </div>
                    <div class="mb-3">
                        {{ form.password.label(class="form-label") }}
                        {{ form.password(class="form-control" + (" is-invalid" if form.password.errors else ""), id="password") }}
                        <div class="password-strength" id="strength-bar"></div>
                        <small class="form-text text-muted">
                            Must contain uppercase, lowercase, digit, and special character (min 8 chars)
                        </small>
                        {% if form.password.errors %}
                            <div class="invalid-feedback d-block">{{ form.password.errors[0] }}</div>
                        {% endif %}
                    </div>
                    <div class="mb-3">
                        {{ form.confirm_password.label(class="form-label") }}
                        {{ form.confirm_password(class="form-control" + (" is-invalid" if form.confirm_password.errors else "")) }}
                        {% if form.confirm_password.errors %}
                            <div class="invalid-feedback">{{ form.confirm_password.errors[0] }}</div>
                        {% endif %}
                    </div>
                    {{ form.submit(class="btn btn-primary w-100") }}
                </form>
                <hr>
                <div class="text-center">
                    <p>Already have an account? <a href="{{ url_for('auth.login') }}">Login here</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
{% block scripts %}
<script>
document.getElementById('password').addEventListener('input', function(e) {
    const password = e.target.value;
    const strengthBar = document.getElementById('strength-bar');
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\\d/.test(password)) strength++;
    if (/[!@#$%^&*()_+\\-=\\[\\]{}|;:,.<>?]/.test(password)) strength++;
    strengthBar.className = 'password-strength';
    if (strength <= 1) strengthBar.classList.add('strength-weak');
    else if (strength <= 3) strengthBar.classList.add('strength-medium');
    else strengthBar.classList.add('strength-strong');
});
</script>
{% endblock %}
"""

# Account template
account_html = """{% extends "base.html" %}
{% block title %}My Account{% endblock %}
{% block content %}
<div class="row mt-5">
    <div class="col-md-8 offset-md-2">
        <h2>👤 My Account</h2>
        <div class="card mt-4">
            <div class="card-body">
                <h5 class="card-title">Account Information</h5>
                <p><strong>Name:</strong> {{ user.full_name }}</p>
                <p><strong>Email:</strong> {{ user.email }}</p>
                <p><strong>Role:</strong> {{ user.role }}</p>
                <p><strong>2FA Status:</strong> 
                    {% if user.is_2fa_enabled %}
                        <span class="badge bg-success">Enabled</span>
                    {% else %}
                        <span class="badge bg-secondary">Disabled</span>
                    {% endif %}
                </p>
                <p><strong>Last Login:</strong> {{ user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never' }}</p>
            </div>
        </div>
        <div class="card mt-4">
            <div class="card-body">
                <h5 class="card-title">Security Settings</h5>
                <div class="d-grid gap-2">
                    <a href="{{ url_for('auth.change_password') }}" class="btn btn-outline-primary">Change Password</a>
                    {% if user.is_2fa_enabled %}
                        <a href="{{ url_for('auth.disable_2fa') }}" class="btn btn-outline-warning">Disable 2FA</a>
                    {% else %}
                        <a href="{{ url_for('auth.setup_2fa') }}" class="btn btn-outline-success">Enable 2FA</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# Write all templates
templates = {
    'app/templates/base.html': base_html,
    'app/templates/auth/login.html': login_html,
    'app/templates/auth/register.html': register_html,
    'app/templates/auth/account.html': account_html,
}

for path, content in templates.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {path}")

print("\n✅ Core templates created successfully!")
print("\nNote: Additional templates need to be created manually or run the full template generator.")
print("See AUTH_README.md for complete documentation.")
