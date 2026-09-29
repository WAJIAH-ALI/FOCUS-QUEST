from typing import Optional
import redis.asyncio as aioredis
import redis
from app.core.config import settings

_async_redis_client: Optional[aioredis.Redis] = None
_sync_redis_client: Optional[redis.Redis] = None


async def get_async_redis() -> aioredis.Redis:
    global _async_redis_client
    if _async_redis_client is None:
        _async_redis_client = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return _async_redis_client


def get_sync_redis() -> redis.Redis:
    global _sync_redis_client
    if _sync_redis_client is None:
        _sync_redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return _sync_redis_client
