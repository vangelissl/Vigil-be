from celery import Celery

from vigil.core.config import settings


celery = Celery("vigil", broker=settings.celery_broker_url,
                task_ignore_result=True)

celery.conf.update(
    task_ignore_result=True,
    task_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "run_inference": {"queue": "ml"},
    },
)
