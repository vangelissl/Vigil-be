from abc import ABC, abstractmethod

import uuid

from .domain.value_objects import ClassificationResult
from ..videos.ports import VideoRepositoryProtocol
from ...core.database.session import AsyncSession

from ..analysis.domain.entities import Analysis

class MLClassifierProtocol(ABC):
	def __init__(self, video_repository: VideoRepositoryProtocol):
		self.video_repository = video_repository

	@abstractmethod
	async def predict(self, video_path: str) -> ClassificationResult:
		pass


class AnalysisRepositoryProtocol(ABC):
	def __init__(self, session: AsyncSession):
		self.session = session

	@abstractmethod
	async def get(self, analysis_id: uuid.UUID) -> Analysis | None:
		pass		

	@abstractmethod
	async def create(self, analysis: Analysis) -> Analysis:
		pass

	@abstractmethod
	async def delete(self, analysis_id: uuid.UUID) -> bool:
		pass

	@abstractmethod
	async def get_all_by_owner(self, owner_id: uuid.UUID) -> list[Analysis]:
		pass

	@abstractmethod
	async def update(self, analysis: Analysis):
		pass