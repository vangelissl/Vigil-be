from ....shared.base import Entity

from ...users.domain.value_objects import UserId

from .value_objects import VideoId, VideoStatus, Filename, SizeBytes

class Video(Entity):

	def __init__(self, id: VideoId, owner_id: UserId, filename: Filename, size_bytes: SizeBytes, status: VideoStatus, minio_path: str):
		self.id: VideoId = id
		self.owner_id: UserId = owner_id
		self.filename: Filename = filename
		self.size_bytes: SizeBytes = size_bytes
		self.status: VideoStatus = status
		self.minio_path: str = minio_path