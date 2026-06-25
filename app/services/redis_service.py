import os
import redis

class SimpleCache:
    """In-memory fallback if Redis is unavailable"""
    def __init__(self):
        self.data = {}

    def set(self, key, value, ex=None):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def delete(self, key):
        if key in self.data:
            del self.data[key]

try:
    REDIS_URL = os.getenv("REDIS_URL")

    redis_client = redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5
    )

    redis_client.ping()
    print("✅ Redis connected successfully")

except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    print("DEBUG: Redis unavailable. Using in-memory fallback for session state.")
    redis_client = SimpleCache()