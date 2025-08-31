import json
import redis
from typing import Dict, List, Optional, Union, Any

from src.util.utilities import get_redis_client


class RedisConversationRetriever:
    """
    A class to retrieve conversation data from Redis cache using a specific key pattern.
    """

    def __init__(
            self,
            key_prefix: str = "prometa_ai:conversation:"
    ):
        self.redis_client = get_redis_client()
        self.key_prefix = key_prefix

    def get_conversation(self, user_email: str) -> Optional[Dict[str, Any]]:
        """ Retrieve a conversation for a specific user.       """
        key = f"{self.key_prefix}{user_email}"
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON data for key: {key}")
            return None
        except redis.RedisError as e:
            print(f"Redis error when retrieving key {key}: {e}")
            return None

    def get_all_conversations(self, pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """ Retrieve all conversations matching a pattern.        """
        search_pattern = f"{self.key_prefix}{pattern or '*'}"
        conversations = []

        try:
            keys = self.redis_client.keys(search_pattern)
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    try:
                        conversations.append(json.loads(data))
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON data for key: {key}")
        except redis.RedisError as e:
            print(f"Redis error when retrieving conversations: {e}")

        return conversations

    def delete_conversation(self, user_email: str) -> bool:
        """
        Delete a conversation for a specific user.
        """
        key = f"{self.key_prefix}{user_email}"
        try:
            return bool(self.redis_client.delete(key))
        except redis.RedisError as e:
            print(f"Redis error when deleting key {key}: {e}")
            return False

    def close(self):
        """Close the Redis connection."""
        self.redis_client.close()
