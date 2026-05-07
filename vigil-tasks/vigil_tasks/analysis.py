from celery import shared_task


@shared_task(name="run_inference")
def run_inference(analysis_id: str) -> None:
	print(f"Received analysis_id: {analysis_id}")