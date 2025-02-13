import json
from typing import Optional, Any
from redis.asyncio import Redis
from app.core.config import settings

# Create Redis connection pool
redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

async def set_cache(key: str, value: Any, expire: Optional[int] = None) -> None:
    """Set a cache value with optional expiration"""
    expire = expire or settings.CACHE_TTL
    await redis.set(key, json.dumps(value), ex=expire)

async def get_cache(key: str) -> Optional[Any]:
    """Get a cached value"""
    data = await redis.get(key)
    if data:
        return json.loads(data)
    return None

async def delete_cache(key: str) -> None:
    """Delete a cached value"""
    await redis.delete(key)

async def clear_cache() -> None:
    """Clear all cached values"""
    await redis.flushdb()

def generate_cache_key(prefix: str, **kwargs) -> str:
    """Generate a cache key from prefix and parameters"""
    params = sorted(kwargs.items())
    param_str = "_".join(f"{k}:{v}" for k, v in params)
    return f"{prefix}:{param_str}" 