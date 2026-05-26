from ....shared.base import Entity

from .value_objects import AnalysisStatus, ClassificationResult

from ...videos.domain.value_objects import VideoId

from .exceptions import InvalidAnalysisStateTransition

class Analysis(Entity):
	def __init__(self, status: AnalysisStatus, video_id: VideoId, classification_result: ClassificationResult):
		self.status = status
		self.video_id = video_id
		self.classification_result = classification_result

	def start_processing(self):
		if self.status != AnalysisStatus.PENDING:
			raise InvalidAnalysisStateTransition(f"Cannot start processing from {self.status}")
		self.status = AnalysisStatus.PROCESSING

	def complete_processing(self):
		if self.status != AnalysisStatus.PROCESSING:
			raise InvalidAnalysisStateTransition(f"Cannot complete processing from {self.status}")
		self.status = AnalysisStatus.COMPLETED

	def mark_as_failed(self):
		if self.status in [AnalysisStatus.COMPLETED, AnalysisStatus.FAILED]:
			raise InvalidAnalysisStateTransition("Analysis is already completed or failed")
		self.status = AnalysisStatus.FAILED

		