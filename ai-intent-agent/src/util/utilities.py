import os
import json
import redis
from datetime import timedelta
from typing import Optional
from langchain_openai import ChatOpenAI

from src.config.config import AppConfig

def get_redis_client():
    try:
        client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 15)),
            decode_responses=True
        )

        client.ping()
        print("Connected to Redis")
        return client
    except redis.ConnectionError as e:
        print(f"Redis connection failed: {e}")
        raise


def cache_bizigo_headers(headers: dict, ttl_minutes: int = 15):
    """Cache user authentication headers"""
    try:
        user_id = headers.get("UserId", "default_user")
        application_id = headers.get("ApplicationId", "default_session")
        key = f"user:{user_id}:applicationid:{application_id}:auth"
        value = json.dumps(headers)
        ttl = timedelta(minutes=ttl_minutes)
        redis_client = get_redis_client()

        redis_client.setex(key, ttl, value)
        print(f"[CACHE] Stored auth headers in Redis: {key}")
        return True
    except Exception as e:
        print(f"[CACHE] Failed to store auth headers: {e}")
        return False


def get_cached_headers(user_id: str, application_id:str, session_id: str) -> Optional[dict]:
    """Retrieve cached auth headers"""
    try:
        redis_client = get_redis_client()
        key = f"user:{user_id}:applicationid:{application_id}:auth"
        value = redis_client.get(key)

        if value:
            print(f"[CACHE] Retrieved auth headers from Redis: {key}")
            return json.loads(value)
        return None
    except Exception as e:
        print(f"[CACHE] Failed to retrieve auth headers: {e}")
        return None






