import redis.asyncio as redis
import json
import os
from typing import Optional, Dict, Any


class RedisClient:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_pool = None

    async def connect(self):
        self.redis_pool = redis.ConnectionPool.from_url(self.redis_url)

    async def disconnect(self):
        if self.redis_pool:
            await self.redis_pool.disconnect()

    async def get_redis(self) -> redis.Redis:
        return redis.Redis(connection_pool=self.redis_pool)


# Global client instance
redis_client = RedisClient(os.getenv("REDIS_URL", "redis://localhost:6379"))


async def get_redis() -> redis.Redis:
    return await redis_client.get_redis()


# Helper functions for JSON storage
async def set_json(
    key: str, data: Dict[Any, Any], redis_conn: redis.Redis, expire: int = None
):
    """Store JSON data in Redis"""
    json_data = json.dumps(data, default=str)
    if expire:
        await redis_conn.setex(key, expire, json_data)
    else:
        await redis_conn.set(key, json_data)


async def get_json(key: str, redis_conn: redis.Redis) -> Optional[Dict[Any, Any]]:
    """Retrieve JSON data from Redis"""
    data = await redis_conn.get(key)
    if data:
        return json.loads(data)
    return None
