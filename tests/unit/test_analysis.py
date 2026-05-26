import pytest

from typing import Callable

import uuid

from vigil.modules.analysis.domain.entities import Analysis, UserId, VideoId
from vigil.modules.analysis.domain.value_objects import AnalysisId, AnalysisStatus, ClassificationResult
from vigil.modules.analysis.domain.exceptions import InvalidClassificationScore, InvalidAnalysisStateTransition


analysis = Analysis(
    id=AnalysisId(uuid.uuid4()),
    owner_id=UserId(uuid.uuid4()),
    video_id=VideoId(uuid.uuid4()),
    status=AnalysisStatus.PENDING
)


@pytest.mark.parametrize("score, raises_exception", [
    (0, False),
    (0.01, False),
    (0.5, False),
    (0.999, False),
    (1, False),
    (-1, True),
    (5, True)
])
def test_classification_result_create(score: float, raises_exception: bool):
    if raises_exception:
        with pytest.raises(InvalidClassificationScore):
            classification_result = ClassificationResult(score)
    else:
        classification_result = ClassificationResult(score)

        assert classification_result is not None
        assert classification_result.value == score


@pytest.mark.parametrize("prev_status, new_status, method, raises_exception", [
    (AnalysisStatus.PENDING, AnalysisStatus.PROCESSING,
     analysis.start_processing, False),
    (AnalysisStatus.PENDING, AnalysisStatus.COMPLETED,
     analysis.complete_processing, True),
    (AnalysisStatus.PENDING, AnalysisStatus.FAILED, analysis.mark_as_failed, False),
    (AnalysisStatus.PROCESSING, AnalysisStatus.PROCESSING,
     analysis.start_processing, True),
    (AnalysisStatus.PROCESSING, AnalysisStatus.COMPLETED,
     analysis.complete_processing, False),
    (AnalysisStatus.PROCESSING, AnalysisStatus.FAILED, analysis.mark_as_failed, False),
    (AnalysisStatus.COMPLETED, AnalysisStatus.PROCESSING,
     analysis.start_processing, True),
    (AnalysisStatus.COMPLETED, AnalysisStatus.COMPLETED,
     analysis.complete_processing, True),
    (AnalysisStatus.COMPLETED, AnalysisStatus.FAILED, analysis.mark_as_failed, True),
    (AnalysisStatus.FAILED, AnalysisStatus.PROCESSING,
     analysis.start_processing, True),
    (AnalysisStatus.FAILED, AnalysisStatus.COMPLETED,
     analysis.complete_processing, True),
    (AnalysisStatus.FAILED, AnalysisStatus.FAILED, analysis.mark_as_failed, True)
])
def test_analysis_state_transition(prev_status: AnalysisStatus, new_status: AnalysisStatus, method: Callable, raises_exception: bool):
    analysis.status = prev_status

    if raises_exception:
        with pytest.raises(InvalidAnalysisStateTransition):
            if new_status == AnalysisStatus.COMPLETED:
                method(ClassificationResult(0.1))
            method()
    else:
        if new_status == AnalysisStatus.COMPLETED:
            method(ClassificationResult(0.1))
        else:
            method()

        assert analysis.status == new_status


def test_analysis_create():
    analysis = Analysis(
        id=AnalysisId(uuid.uuid4()),
        owner_id=UserId(uuid.uuid4()),
        video_id=VideoId(uuid.uuid4()),
        status=AnalysisStatus.PENDING
    )

    assert analysis is not None