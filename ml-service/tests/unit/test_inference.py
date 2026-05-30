import pytest
from unittest.mock import MagicMock, patch
import torch

from worker.inference import Recognizer
from worker.result import ClassificationResult


@pytest.fixture
def mock_model():
    """Mock MMAction2 model"""
    return MagicMock()


@pytest.fixture
def mock_action_data_sample():
    """Mock ActionDataSample result"""
    sample = MagicMock()
    sample.all_items.return_value = {
        "pred_label": torch.tensor([1]),
        "pred_score": torch.tensor([0.2, 0.8])
    }
    return sample


@pytest.fixture
def recognizer(mock_model):
    """Recognizer with mocked model"""
    with patch('worker.inference.init_recognizer', return_value=mock_model):
        recognizer = Recognizer("config.py", "checkpoint.pth", "cpu")
    return recognizer


def test_run_inference_returns_classification_result(recognizer, mock_action_data_sample):
    """Should return ClassificationResult with correct structure"""
    with patch('worker.inference.inference_recognizer', return_value=mock_action_data_sample):
        result = recognizer.run_inference(
            "video.mp4",
            labels=["non_violent", "violent"]
        )
    
    assert isinstance(result, ClassificationResult)
    assert result.predicted_class == "violent"
    assert result.confidence > 0.0 and result.confidence <= 1.0
    assert "non_violent" in result.all_scores
    assert "violent" in result.all_scores


def test_inference_applies_temperature_scaling(recognizer, mock_action_data_sample):
    """Should smooth extreme confidence values with temperature scaling"""
    with patch('worker.inference.inference_recognizer', return_value=mock_action_data_sample):
        result = recognizer.run_inference(
            "video.mp4",
            labels=["non_violent", "violent"],
            temperature=2.0
        )
    
    # With temperature scaling, confidence shouldn't be 1.0
    assert result.confidence < 1.0
    # But should still be confident (class 1 had higher score)
    assert result.confidence > 0.5


def test_scores_sum_to_one(recognizer, mock_action_data_sample):
    """All scores should sum to approximately 1.0 (probability distribution)"""
    with patch('worker.inference.inference_recognizer', return_value=mock_action_data_sample):
        result = recognizer.run_inference(
            "video.mp4",
            labels=["non_violent", "violent"]
        )
    
    total = sum(result.all_scores.values())
    assert abs(total - 1.0) < 0.01  # allow small floating point error