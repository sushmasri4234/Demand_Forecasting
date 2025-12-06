"""
Flask application factory.
"""
import os
from flask import Flask
from config import Config
from app.extensions import (
    db, migrate, login_manager, mail, csrf, limiter, talisman,
    init_login_manager
)
from app.utils import setup_logging


def create_app(config_class=Config):
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    init_login_manager(app)
    mail.init_app(app)
    csrf.init_app(app)
    
    # Initialize rate limiter with Redis
    limiter.init_app(app)
    
    # Initialize Talisman for security headers
    if app.config.get('FORCE_HTTPS', False):
        talisman.init_app(app, force_https=True)
    else:
        talisman.init_app(app, force_https=False)
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    from app.auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from app.main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        from app.models import User
        admin = User.query.filter_by(email='admin@demandforecasting.com').first()
        if not admin:
            admin = User(
                email='admin@demandforecasting.com',
                full_name='Admin User',
                role='admin',
                is_active=True,
                is_verified=True
            )
            admin.set_password('Admin@123456')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            app.logger.info('Default admin user created')
    
    return app
