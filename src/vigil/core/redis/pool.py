from redis.asyncio import ConnectionPool

from vigil.core.config import settings

pool = ConnectionPool.from_url(
	settings.redis_url,
	max_connections=20,
	decode_responses=True,
)