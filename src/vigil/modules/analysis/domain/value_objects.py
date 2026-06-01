from enum import Enum

import uuid

from dataclasses import asdict, dataclass

from ....shared.base import ValueObject

from .exceptions import NegativeScoreError, ScoreGreaterThanOneError


@dataclass(frozen=True)
class AnalysisId(ValueObject):
    value: uuid.UUID


class AnalysisStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class ClassificationResult:
    predicted_class: str
    confidence: float
    all_scores: dict[str, float]

    def __post_init__(self):
        if self.all_scores[self.predicted_class] < 0.0:
            raise NegativeScoreError()
        if self.all_scores[self.predicted_class] > 1.0:
            raise ScoreGreaterThanOneError()

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "ClassificationResult":
        return ClassificationResult(**data)
