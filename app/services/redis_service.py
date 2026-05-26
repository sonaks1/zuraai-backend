import redis
import json

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
    redis_client = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
        socket_connect_timeout=1
    )
    redis_client.ping()
    print("DEBUG: Using Redis for session state.")
except Exception:
    print("DEBUG: Redis unavailable. Using in-memory fallback for session state.")
    redis_client = SimpleCache()