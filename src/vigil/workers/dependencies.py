from .celery_app import Celery, celery


async def get_celery() -> Celery:
	return celery