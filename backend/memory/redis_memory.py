import redis
from config import REDIS_URL

redis_client = redis.Redis.from_url(REDIS_URL)


def store_state(key, value):
    redis_client.set(key, value)


def get_state(key):
    return redis_client.get(key)