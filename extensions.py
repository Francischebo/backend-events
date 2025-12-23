# extensions.py - Flask Extensions Initialization
from flask_pymongo import PyMongo
import os
import pymongo
from config import Config
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt

# Initialize extensions
class _MongoWrapper:
	"""Wrapper around Flask-PyMongo to provide a reliable `db` attribute.

	Some MongoDB URIs (notably mongodb+srv without a path) may not expose a default
	database to Flask-PyMongo. This wrapper ensures `mongo.db` is always available
	after `init_app(app)` by falling back to a direct `pymongo.MongoClient` when needed.
	"""
	def __init__(self):
		self._py = PyMongo()
		self.db = None
		self.client = None

	def init_app(self, app):
	    uri = app.config.get('MONGO_URI') or os.environ.get('MONGO_URI') or Config.MONGO_URI
	    dbname = app.config.get('MONGO_DBNAME') or os.environ.get('MONGO_DBNAME') or getattr(Config, 'MONGO_DBNAME', 'event_management')
	    
	    try:
	        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=20000)
	        client.admin.command('ping')  # safer than server_info() in some cases
	        self.client = client
	        self.db = client[dbname]
	        app.logger.info(f"✅ Connected to MongoDB Atlas: {dbname}")
	    except Exception as e:
	        app.logger.error(f"❌ Failed to connect to MongoDB Atlas: {e}")

	def __getattr__(self, name):
		# Proxy other attributes/methods to the underlying PyMongo instance
		return getattr(self._py, name)


mongo = _MongoWrapper()
jwt = JWTManager()
# Do not force `async_mode` here – allow Flask-SocketIO to auto-detect the best
# available async framework (eventlet/gevent) for production performance.
socketio = SocketIO()
bcrypt = Bcrypt()
