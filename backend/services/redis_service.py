import json
import redis.asyncio as aioredis

redis_client = aioredis.from_url("redis://127.0.0.1:6379", decode_responses=True)

async def get_cache(key: str):
    try:
        val = await redis_client.get(key)
        return json.loads(val) if val else None
    except Exception:
        return None

async def set_cache(key: str, value, ttl: int = 60):
    try:
        await redis_client.set(key, json.dumps(value), ex=ttl)
    except Exception:
        pass

async def invalidate_cache(pattern: str):
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
    except Exception:
        pass
