from abc import ABC, abstractmethod
from .domain.value_objects import ClassificationResult
from ..videos.ports import VideoRepositoryProtocol

class MLClassifierProtocol(ABC):
	def __init__(self, video_repository: VideoRepositoryProtocol):
		self.video_repository = video_repository

	@abstractmethod
	async def predict(self, video_path: str) -> ClassificationResult:
		pass