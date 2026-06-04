from celery import shared_task


@shared_task(name="run_inference")
def run_inference(analysis_id: str) -> None:
	raise NotImplementedError("This is a stub. Ml-worker has the implementation.")