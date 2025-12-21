# config.py - Application Configuration
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # MongoDB URI (read from environment)
    MONGO_URI = os.environ.get('MONGO_URI')
    MONGO_DBNAME = os.environ.get('MONGO_DBNAME') or 'event_management'

    # MongoDB Connection Pool Settings
    MONGO_MAX_POOL_SIZE = int(os.environ.get('MONGO_MAX_POOL_SIZE') or 50)
    MONGO_MIN_POOL_SIZE = int(os.environ.get('MONGO_MIN_POOL_SIZE') or 10)
    MONGO_MAX_IDLE_TIME_MS = int(os.environ.get('MONGO_MAX_IDLE_TIME_MS') or 30000)
    MONGO_SERVER_SELECTION_TIMEOUT_MS = int(os.environ.get('MONGO_SERVER_SELECTION_TIMEOUT_MS') or 5000)
    MONGO_CONNECT_TIMEOUT_MS = int(os.environ.get('MONGO_CONNECT_TIMEOUT_MS') or 5000)
    MONGO_SOCKET_TIMEOUT_MS = int(os.environ.get('MONGO_SOCKET_TIMEOUT_MS') or 5000)

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Flask Performance Settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_TYPE = 'filesystem'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # File uploads
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or './uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Firebase
    FIREBASE_SERVICE_ACCOUNT_KEY = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY')

    # Email config
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Geofencing
    DEFAULT_GEOFENCE_RADIUS = 200
    REQUEST_TIMEOUT_MS = int(os.environ.get('REQUEST_TIMEOUT_MS') or 3000)  # Reduced from 5000

    # Performance Settings
    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_MAX_OVERFLOW = 30
    SQLALCHEMY_POOL_TIMEOUT = 10
    SQLALCHEMY_POOL_RECYCLE = 3600


class DevelopmentConfig(Config):
    DEBUG = True
    FIREBASE_SERVICE_ACCOUNT_KEY = None  # Disable Firebase locally
    MONGO_URI = os.environ.get('MONGO_URI') 

class ProductionConfig(Config):
    DEBUG = False
    # Must provide Atlas URI in environment
    MONGO_URI = os.environ.get('MONGO_URI')
    if not MONGO_URI:
        raise ValueError("MONGO_URI environment variable is required for production")
