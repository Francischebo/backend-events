# app.py
import os
import json
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

from flask_compress import Compress

from extensions import mongo, jwt, socketio, bcrypt
from routes import register_blueprints
from websocket_handlers import register_socketio_handlers
from config import DevelopmentConfig, ProductionConfig, TestingConfig

load_dotenv()

def create_app(config_name=None):
    app = Flask(__name__)

    # ---------------- CONFIG ----------------
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "production")

    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    app.config.from_object(config_map.get(config_name, ProductionConfig))

    # ---------------- PERFORMANCE OPTIMIZATIONS ----------------
    # Enable gzip compression
    compress = Compress()
    compress.init_app(app)

    # Request timeout settings
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    app.config['SESSION_TYPE'] = 'filesystem'

    # ---------------- MONGODB ----------------
    app.config["MONGO_URI"] = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI") or app.config.get("MONGO_URI")
    mongo.init_app(app)

    # ---------------- EXTENSIONS ----------------
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "max_age": 86400
        }
    })
    jwt.init_app(app)
    bcrypt.init_app(app)

    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode="threading",
        ping_timeout=10,
        ping_interval=25,
        max_http_buffer_size=1000000
    )

    # ---------------- FIREBASE ----------------
    if not firebase_admin._apps:
        key_path = app.config.get("FIREBASE_SERVICE_ACCOUNT_KEY")
        if key_path:
            try:
                cred = (
                    credentials.Certificate(key_path)
                    if os.path.exists(key_path)
                    else credentials.Certificate(json.loads(key_path))
                )
                firebase_admin.initialize_app(cred)
            except Exception:
                pass  # silent in production

    # ---------------- ROUTES ----------------
    register_blueprints(app)
    register_socketio_handlers(socketio)

    # ---------------- SAFE INDEX CREATION ----------------
    def ensure_indexes():
        try:
            mongo.db.users.create_index("email", unique=True)
            mongo.db.users.create_index("username", unique=True)
            mongo.db.events.create_index([("location", "2dsphere")])
        except Exception:
            pass  # NEVER crash or log TLS noise

    @app.before_request
    def lazy_index_init():
        if not getattr(app, "_indexes_initialized", False):
            app._indexes_initialized = True
            ensure_indexes()

    return app


app = create_app()

# ---------------- GUNICORN ENTRY ----------------
if __name__ == "__main__":
    bind_host = os.environ.get("BIND_HOST", "0.0.0.0")
    bind_port = int(os.environ.get("PORT", 8080))

    socketio.run(
        app,
        host=bind_host,
        port=bind_port,
        debug=app.debug,
        use_reloader=False
    )
