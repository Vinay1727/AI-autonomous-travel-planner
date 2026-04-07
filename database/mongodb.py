# MongoDB connection utility for Premium AI Travel

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Delay connection until explicitly requested to avoid blocking imports
        pass
    
    def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            mongodb_uri = os.getenv('MONGODB_URI')
            db_name = os.getenv('MONGODB_DB_NAME', 'luxetravel')
            
            if not mongodb_uri:
                raise ValueError("MONGODB_URI not found in environment variables")

            self._client = MongoClient(mongodb_uri)
            # Test connection
            self._client.admin.command('ping')
            self._db = self._client[db_name]

            # Create indexes
            self._create_indexes()

            print(f"✅ Connected to MongoDB Atlas - Database: {db_name}")

        except ConnectionFailure as e:
            print(f"❌ MongoDB connection failed: {e}")
            # Do not raise here; leave _client as None and let callers handle missing DB
            self._client = None
            self._db = None
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            self._client = None
            self._db = None
    
    def _create_indexes(self):
        """Create necessary indexes"""
        # Unique index on email
        self._db.users.create_index("email", unique=True)
        # Index on created_at for sorting
        self._db.users.create_index("created_at")
    
    def get_database(self):
        """Get database instance"""
        if self._db is None and self._client is None:
            # Try connecting once; if it fails, return None so callers can fallback
            try:
                self.connect()
            except Exception:
                return None
        return self._db
    
    def get_collection(self, collection_name):
        """Get collection instance"""
        return self.get_database()[collection_name]
    
    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            print("✅ MongoDB connection closed")

# Singleton instance
mongodb = None


class InMemoryCollection:
    def __init__(self):
        self._data = []

    def find_one(self, query):
        for d in self._data:
            match = True
            for k, v in query.items():
                if d.get(k) != v:
                    match = False
                    break
            if match:
                return d
        return None

    def insert_one(self, doc):
        # mimic pymongo InsertOneResult by returning inserted id
        self._data.append(doc.copy())
        return True

    def delete_one(self, query):
        for i, d in enumerate(self._data):
            match = True
            for k, v in query.items():
                if d.get(k) != v:
                    match = False
                    break
            if match:
                del self._data[i]
                return True
        return False

    def delete_many(self, query):
        to_delete = [d for d in self._data if all(d.get(k) == v for k, v in query.items())]
        for d in to_delete:
            self._data.remove(d)
        return True

    def create_index(self, *args, **kwargs):
        return True


def _get_mongodb_singleton():
    global mongodb
    if mongodb is None:
        mongodb = MongoDB()
    return mongodb


def get_users_collection():
    """Get users collection; returns in-memory fallback if DB not available"""
    m = _get_mongodb_singleton()
    try:
        coll = m.get_collection('users') if m.get_database() is not None else None
    except Exception:
        coll = None

    if coll is None:
        # Return an in-memory collection as fallback
        if not hasattr(m, '_users_fallback') or m._users_fallback is None:
            m._users_fallback = InMemoryCollection()
        return m._users_fallback
    return coll


def get_otp_collection():
    """Get OTP collection (temporary storage); in-memory fallback if DB unavailable"""
    m = _get_mongodb_singleton()
    try:
        coll = m.get_collection('otp_verifications') if m.get_database() is not None else None
    except Exception:
        coll = None

    if coll is None:
        if not hasattr(m, '_otp_fallback') or m._otp_fallback is None:
            m._otp_fallback = InMemoryCollection()
        return m._otp_fallback
    return coll
