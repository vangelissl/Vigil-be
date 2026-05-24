# core/storage.py
import io
import uuid
from minio import Minio
from fastapi import UploadFile


class MinioStorage:
    def __init__(self, client: Minio, bucket: str):
        self.client = client
        self.bucket = bucket
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    async def upload(self, file: UploadFile) -> str:
        contents = await file.read()
        object_name = f"{uuid.uuid4()}{file.filename}"
        
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=io.BytesIO(contents),
            length=file.size if file.size else 0,
            content_type=file.content_type if file.content_type else "unknown"
        )
        return object_name

    def delete(self, object_name: str) -> None:
        self.client.remove_object(self.bucket, object_name)

    def get_url(self, object_name: str) -> str:
        return self.client.presigned_get_object(self.bucket, object_name)