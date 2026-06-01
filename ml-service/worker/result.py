from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationResult:
    predicted_class: str
    confidence: float
    all_scores: dict[str, float]
