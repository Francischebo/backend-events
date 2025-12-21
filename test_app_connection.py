#!/usr/bin/env python3
"""
Test Atlas connection using the same logic as the Flask app
"""
import pymongo

# Set the URI
MONGO_URI = 'mongodb+srv://francischeboo404_db_user:Fr%40m0ng00se387623@communityapp.ktglocw.mongodb.net/event_management?retryWrites=true&w=majority&ssl=true'
MONGO_DBNAME = 'event_management'

print("Testing Atlas connection with app-like settings...")

try:
    # Create client (same as extensions.py)
    client = pymongo.MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        tls=True,
        tlsAllowInvalidCertificates=False
    )

    print("Client created, testing connection...")
    # Test connection
    server_info = client.server_info()
    print(f"✅ Connected! MongoDB version: {server_info.get('version', 'unknown')}")

    # Get database
    db = client[MONGO_DBNAME]
    print(f"✅ Database: {db.name}")

    # List collections
    collections = db.list_collection_names()
    print(f"✅ Collections: {collections}")

except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()