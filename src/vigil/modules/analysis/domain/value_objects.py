from enum import Enum

import uuid

from dataclasses import dataclass

from ....shared.base import ValueObject

from .exceptions import NegativeScoreError, ScoreGreaterThanOneError


@dataclass(frozen=True)
class AnalysisId(ValueObject):
	value: uuid.UUID


class AnalysisStatus(Enum):
	PENDING = "pending"
	PROCESSING = "processing"
	COMPLETED  = "completed"
	FAILED = "failed"


@dataclass(frozen=True)
class ClassificationResult(ValueObject):
	value: float

	def __post_init__(self):
		if self.value < 0:
			raise NegativeScoreError()
		
		if self.value > 1:
			raise ScoreGreaterThanOneError()