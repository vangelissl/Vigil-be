from datetime import UTC, datetime

from ....shared.base import Entity

from .value_objects import AnalysisStatus, ClassificationResult, AnalysisId

from ...videos.domain.value_objects import VideoId
from ...users.domain.value_objects import UserId

from .exceptions import InvalidAnalysisStateTransition

class Analysis(Entity):
	def __init__(self, id: AnalysisId, owner_id: UserId, status: AnalysisStatus, video_id: VideoId, classification_result: ClassificationResult | None = None, created_at: datetime | None = None, completed_at: datetime | None = None):
		self.id = id
		self.video_id = video_id
		self.owner_id = owner_id
		self.classification_result = classification_result
		self.status = status
		self.created_at = created_at or datetime.now(UTC)
		self.completed_at = completed_at

	def start_processing(self):
		if self.status != AnalysisStatus.PENDING:
			raise InvalidAnalysisStateTransition(f"Cannot start processing from {self.status}")
		self.status = AnalysisStatus.PROCESSING

	def complete_processing(self, result: ClassificationResult):
		if self.status != AnalysisStatus.PROCESSING:
			raise InvalidAnalysisStateTransition(f"Cannot complete processing from {self.status}")
		self.classification_result = result
		self.status = AnalysisStatus.COMPLETED
		self.completed_at = datetime.now(UTC)

	def mark_as_failed(self):
		if self.status in [AnalysisStatus.COMPLETED, AnalysisStatus.FAILED]:
			raise InvalidAnalysisStateTransition("Analysis is already completed or failed")
		self.status = AnalysisStatus.FAILED