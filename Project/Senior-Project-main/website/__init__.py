from flask import Flask as fs
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def create_app(secrete_key: str):
    app = fs(__name__)
    
    # Use the secret key passed from main config
    app.secret_key = secrete_key
    
    # Database configuration from environment
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///user_data.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    from .models import db
    db.init_app(app)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')

    return app
