import pytest
import os
from pathlib import Path
from worker.inference import Recognizer
from worker.result import ClassificationResult


PROJECT_ROOT = Path(__file__).parent.parent.parent
MODEL_CONFIG = PROJECT_ROOT / "worker/models/I3D/_settings/config.py"
MODEL_CHECKPOINT = PROJECT_ROOT / "worker/models/I3D/_checkpoints/best_acc_top1_epoch_24.pth"
SAMPLE_VIDEO = PROJECT_ROOT / "tests/integration/sample_video.mp4"

@pytest.fixture
def recognizer():
    """Real recognizer with actual model"""
    # Skip test if model files don't exist
    if not MODEL_CONFIG.exists() or not MODEL_CHECKPOINT.exists():
        pytest.skip("Model files not found")
    
    return Recognizer(str(MODEL_CONFIG), str(MODEL_CHECKPOINT), device="cpu")


@pytest.fixture
def sample_video():
    """Path to a short sample video (you provide this)"""
    if not SAMPLE_VIDEO.exists():
        pytest.skip("Sample video not found")
    return str(SAMPLE_VIDEO)


def test_inference_on_real_video(recognizer, sample_video):
    """Should run inference on real video and return valid result"""
    result = recognizer.run_inference(
        sample_video,
        labels=["non_violent", "violent"]
    )
    
    # Check result structure
    assert isinstance(result, ClassificationResult)
    assert result.predicted_class in ["non_violent", "violent"]
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.all_scores) == 2
    
    # Check probability distribution
    assert abs(sum(result.all_scores.values()) - 1.0) < 0.01 # type: ignore


def test_inference_output_shape(recognizer, sample_video):
    """Result should always have 2 scores (2 classes)"""
    result = recognizer.run_inference(
        sample_video,
        labels=["non_violent", "violent"]
    )
    
    assert len(result.all_scores) == 2
    assert len(result.all_scores) == 2