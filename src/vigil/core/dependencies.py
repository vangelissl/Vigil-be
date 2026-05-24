from fastapi import Depends

from minio import Minio

from redis.asyncio import Redis
from .redis.pool import pool

from .minio.storage import MinioStorage

from .config import settings


async def get_redis() -> Redis:
	return Redis(connection_pool=pool)

async def get_minio_storage() -> MinioStorage:
	client = Minio(
		endpoint=settings.minio_endpoint,
		access_key=settings.minio_access_key,
		secret_key=settings.minio_secret_key,
		secure=settings.minio_secure
	)
	return MinioStorage(client, settings.minio_bucket)