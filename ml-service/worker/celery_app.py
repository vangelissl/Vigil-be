from celery import Celery
import os
from vigil_tasks.analysis import run_inference

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

from .analysis_task import execute_analysis

@celery.task(name="run_inference", bind=True)
async def run_inference_impl(self, analysis_id: str):
	return await execute_analysis(analysis_id)