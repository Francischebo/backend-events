# extensions.py - Flask Extensions Initialization
from flask_pymongo import PyMongo
import os
import pymongo
import ssl
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
		# Initialize the underlying Flask-PyMongo
		self._py.init_app(app)

		# Always use custom client for Atlas connections to ensure proper TLS
		uri = app.config.get('MONGO_URI') or os.environ.get('MONGO_URI') or Config.MONGO_URI
		dbname = app.config.get('MONGO_DBNAME') or os.environ.get('MONGO_DBNAME') or getattr(Config, 'MONGO_DBNAME', 'event_management')
		
		if 'mongodb+srv' in uri or 'atlas' in uri.lower():
			# For Atlas connections, use optimized connection settings
			try:
				client = pymongo.MongoClient(
					uri, 
					serverSelectionTimeoutMS=app.config.get('MONGO_SERVER_SELECTION_TIMEOUT_MS', 5000),
					connectTimeoutMS=app.config.get('MONGO_CONNECT_TIMEOUT_MS', 5000),
					socketTimeoutMS=app.config.get('MONGO_SOCKET_TIMEOUT_MS', 5000),
					maxPoolSize=app.config.get('MONGO_MAX_POOL_SIZE', 50),
					minPoolSize=app.config.get('MONGO_MIN_POOL_SIZE', 10),
					maxIdleTimeMS=app.config.get('MONGO_MAX_IDLE_TIME_MS', 30000),
					retryWrites=True,
					retryReads=True
				)
				# Test connection
				client.server_info()
				self.client = client
				self.db = client[dbname]
				
				# Create optimized indexes for performance
				self._create_indexes()
				
				app.logger.info(f"Connected to MongoDB Atlas: {dbname}")
				return
			except Exception as e:
				app.logger.error(f"Atlas connection failed: {e}")
				self.client = None
				self.db = None
				return
		
		# For non-Atlas connections, try Flask-PyMongo first
		underlying_db = getattr(self._py, 'db', None)
		if underlying_db is not None:
			self.db = underlying_db
			self.client = getattr(self._py, 'cx', None) or getattr(self._py, 'client', None)
			return

		# Fallback: build a pymongo client from config (only for non-Atlas)
		try:
			client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
			# Test connection
			client.server_info()
			self.client = client
			self.db = client[dbname]
			app.logger.info(f"Connected to MongoDB: {dbname}")
		except Exception as e:
			app.logger.error(f"MongoDB connection failed: {e}")
			# Don't raise - let app start without DB for now
			self.client = None
			self.db = None

	def __getattr__(self, name):
		# Proxy other attributes/methods to the underlying PyMongo instance
		return getattr(self._py, name)

	def _create_indexes(self):
		"""Create optimized database indexes for performance"""
		try:
			# User collection indexes
			self.db.users.create_index([("email", 1)], unique=True, background=True)
			self.db.users.create_index([("username", 1)], unique=True, background=True)
			self.db.users.create_index([("role", 1)], background=True)
			self.db.users.create_index([("created_at", -1)], background=True)
			
			# Event collection indexes
			self.db.events.create_index([("creator_id", 1)], background=True)
			self.db.events.create_index([("start_date", 1)], background=True)
			self.db.events.create_index([("end_date", 1)], background=True)
			self.db.events.create_index([("location", "2dsphere")], background=True)
			self.db.events.create_index([("status", 1)], background=True)
			self.db.events.create_index([("created_at", -1)], background=True)
			
			# RSVP collection indexes
			self.db.rsvps.create_index([("user_id", 1)], background=True)
			self.db.rsvps.create_index([("event_id", 1)], background=True)
			self.db.rsvps.create_index([("status", 1)], background=True)
			self.db.rsvps.create_index([("created_at", -1)], background=True)
			
			# Compound indexes for common queries
			self.db.rsvps.create_index([("event_id", 1), ("status", 1)], background=True)
			self.db.rsvps.create_index([("user_id", 1), ("status", 1)], background=True)
			
			print("Database indexes created successfully")
		except Exception as e:
			print(f"Warning: Could not create some indexes: {e}")


mongo = _MongoWrapper()
jwt = JWTManager()
# Do not force `async_mode` here – allow Flask-SocketIO to auto-detect the best
# available async framework (eventlet/gevent) for production performance.
socketio = SocketIO()
bcrypt = Bcrypt()
