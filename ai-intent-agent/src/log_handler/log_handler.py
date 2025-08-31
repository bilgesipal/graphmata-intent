import logging
import asyncio
from datetime import datetime
from redis.asyncio import Redis
from src.config.config import AppConfig


class RedisStreamLogHandler(logging.Handler):
    """Custom log handler that writes logs to a Redis stream."""

    def __init__(self, redis_client: Redis, stream_name: str = "log_channel"):
        super().__init__()
        self.redis_client = redis_client
        self.stream_name = stream_name
        self.service_name = "AI INTENT AGENT"

    def emit(self, record: logging.LogRecord):
        log_data = {
            "service_name": self.service_name,
            "level": record.levelname,
            "message": record.getMessage(),
            "timestamp": datetime.utcnow().isoformat(),
        }

        asyncio.create_task(self._log_to_redis(log_data))

    async def _log_to_redis(self, log_data: dict):
        try:
            msg_id = await self.redis_client.xadd(self.stream_name, log_data)
            key = f"log:{msg_id}"
            await self.redis_client.set(key, str(log_data), ex=1200)
        except Exception as e:
            print(f"[RedisLogHandler] Failed to log: {e}")


def get_logger():
    logger = logging.getLogger("ai-intent-agent")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(console)

    redis_client = Redis.from_url(AppConfig.REDIS_URL, decode_responses=True)
    redis_handler = RedisStreamLogHandler(redis_client, stream_name="log_channel")
    redis_handler.setLevel(logging.INFO)
    logger.addHandler(redis_handler)

    return logger

