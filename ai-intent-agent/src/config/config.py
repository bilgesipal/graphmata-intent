#This file is part of the GraphMata project.
#Trademark (c) 2025 Prometa AI.

import os
import redis.asyncio as aioredis
from dotenv import load_dotenv
load_dotenv()

class AppConfig:

    ENVIRONMENT = os.getenv("ENVIRONMENT", "TEST")
    SERVICE_NAME = os.getenv("SERVICE_NAME", "Intent-Agent")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    NAMESPACE = os.getenv("NAMESPACE", "GraphMata")

    REDIS_HOST = os.getenv("REDIS_HOST", "testredis02.erkaws.com")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_LOG = os.getenv("REDIS_LOG", "service-logs")
    REDIS_DB = int(os.getenv("REDIS_DB", 15))
    REDIS_PUBLISH = os.getenv("REDIS_PUBLISH", "intent-state-update")
    redis_client = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    open_ai_key = os.getenv("OPENAI", "OPENAI")
    REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
