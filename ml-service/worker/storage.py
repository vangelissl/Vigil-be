from minio import Minio
import tempfile
import os


class VideoStorage:
    def __init__(self):
        self.client = Minio(
            endpoint=os.environ["MINIO_ENDPOINT"],
            access_key=os.environ["MINIO_ACCESS_KEY"],
            secret_key=os.environ["MINIO_SECRET_KEY"],
            secure=True if os.environ["MINIO_SECURE"] == "True" else False)
        self.bucket = os.environ["MINIO_BUCKET"]

    async def get(self, minio_path: str):
        """Download video from MinIO to temp file, return path"""
        response = self.client.get_object(
            bucket_name=os.environ["MINIO_BUCKET"],
            object_name=minio_path
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            f.write(response.read())
            return f.name

        response.close()
