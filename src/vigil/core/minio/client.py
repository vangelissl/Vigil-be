from minio import Minio

from vigil.core.config import settings

from pathlib import Path


client = Minio(
    endpoint=settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
	secure=settings.minio_secure
)

def upload_file():
	source_file = Path(__file__).parent / "tmp.txt"
	source_file.write_text("test content")

	bucket_name = settings.minio_bucket
	destination_file = "my.txt"

	found = client.bucket_exists(bucket_name)
	if not found:
		client.make_bucket(bucket_name)
	
	client.fput_object(
		bucket_name, destination_file, str(source_file),
	)

	source_file.unlink()