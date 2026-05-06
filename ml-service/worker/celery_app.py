from celery import Celery
import os


celery = Celery(
    "ml-worker", broker=os.environ["CELERY_BROKER_URL"])

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

# Register analysis task
from vigil_tasks import analysis # noqa: F401