import tempfile
import os
from .db import VideoDatabase
from .storage import VideoStorage
from .inference import Recognizer
from .config import MODEL_CONFIG_PATH, CHECKPOINT_PATH, DEVICE, LABELS


async def execute_analysis(analysis_id: str):
	"""Full analysis task implementation"""
	db = VideoDatabase()
	storage = VideoStorage()
	recognizer = Recognizer(str(MODEL_CONFIG_PATH), str(CHECKPOINT_PATH), DEVICE)

	try:
		db.write_result(analysis_id, "PROCESSING", None)
		
		minio_path = db.get_video_path(analysis_id)
		if not minio_path:
			raise ValueError(f"Analysis {analysis_id} not found")
		
		temp_path = await storage.get(minio_path)

		result = recognizer.run_inference(temp_path, LABELS)

		db.write_result(analysis_id, "COMPLETED", result.to_dict())

		os.unlink(temp_path)

		return {"status": "COMPLETED", "analysis_id": analysis_id}
	
	except Exception as e:
		db.write_result(analysis_id, "FAILED", None)
		raise