import os
from celery import Celery
from .analysis_task import execute_analysis

celery = Celery("ml-worker", broker=os.environ["CELERY_BROKER_URL"])

celery.conf.update(
    task_ignore_result=True,
    task_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "run_inference": {"queue": "ml"},
    },
    worker_pool='solo',
)

# Define the task here, not imported from vigil_tasks
@celery.task(name="run_inference", bind=True)
def run_inference_impl(self, analysis_id: str):
    import asyncio
    return asyncio.run(execute_analysis(analysis_id))