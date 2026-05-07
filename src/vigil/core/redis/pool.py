import redis.asyncio as aioredis

from vigil.core.config import settings

pool = aioredis.ConnectionPool.from_url(
	settings.redis_url,
	max_connections=20,
	decode_responses=True,
)

async def get_redis() -> aioredis.Redis:
	return aioredis.Redis(connection_pool=pool)