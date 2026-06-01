from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ClassificationResult:
    predicted_class: str
    confidence: float
    all_scores: dict[str, float]

    def to_dict(self) -> dict:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> "ClassificationResult":
        return ClassificationResult(**data)