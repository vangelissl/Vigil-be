from redis.asyncio import Redis
from .redis.pool import pool


async def get_redis() -> Redis:
	return Redis(connection_pool=pool)