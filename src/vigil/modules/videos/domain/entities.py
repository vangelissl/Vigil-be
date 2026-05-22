from ....shared.base import Entity

from ...users.domain.value_objects import UserId

from .value_objects import VideoId, VideoStatus, Filename, SizeBytes
from .exceptions import InvalidVideoStateTransition

class Video(Entity):

	def __init__(self, id: VideoId, owner_id: UserId, filename: Filename, size_bytes: SizeBytes, status: VideoStatus, minio_path: str):
		self.id: VideoId = id
		self.owner_id: UserId = owner_id
		self.filename: Filename = filename
		self.size_bytes: SizeBytes = size_bytes
		self.status: VideoStatus = status
		self.minio_path: str = minio_path

	def mark_as_ready(self):
		if self.status != VideoStatus.UPLOADED:
			raise InvalidVideoStateTransition(f"Cannot mark as ready from {self.status}")
		self.status = VideoStatus.READY

	def start_processing(self):
		if self.status != VideoStatus.READY:
			raise InvalidVideoStateTransition(f"Cannot start processing from {self.status}")
		self.status = VideoStatus.PROCESSING

	def complete_processing(self):
		if self.status != VideoStatus.PROCESSING:
			raise InvalidVideoStateTransition(f"Cannot complete processing from {self.status}")
		self.status = VideoStatus.COMPLETED
	
	def mark_as_failed(self):
		if self.status in [VideoStatus.COMPLETED, VideoStatus.FAILED]:
			raise InvalidVideoStateTransition("Video is already completed or failed")
		self.status = VideoStatus.FAILED