import redis
import os
from config import REDIS_URL

def get_redis_connection():
    try:
        client = redis.Redis.from_url(REDIS_URL, socket_connect_timeout=1)
        client.ping()
        return client
    except redis.exceptions.ConnectionError:
        print("REDIS ERROR: Connection failed. Using local fallback.")
        return None

redis_client = get_redis_connection()

def store_state(key, value):
    if redis_client:
        redis_client.set(key, value)

def get_state(key):
    return redis_client.get(key) if redis_client else None