import pytest
import uuid

from collections.abc import Callable

from vigil.shared.exceptions import BusinessRuleValidationException

from vigil.modules.videos.domain.value_objects import VideoId, VideoStatus, Filename, SizeBytes
from vigil.modules.videos.domain.entities import Video, UserId
from vigil.modules.videos.domain.exceptions import InvalidVideoStateTransition


video = Video(
		id=VideoId(uuid.uuid4()),
		owner_id=UserId(uuid.uuid4()),
		filename=Filename("file.mp4"),
		size_bytes=SizeBytes(10),
		status=VideoStatus.UPLOADED,
		minio_path="uri"
	)


@pytest.mark.parametrize("filename_str, raises_exception", [
	("invalid_file.jpeg", True),
	("invalid_file.txt", True),
	("invalid_file.docx", True),
	("invalid_file.mp3", True),
	("invalid_file.py", True),
	("valid_file.mp4", False),
	("valid_file.avi", False),
])
def test_video_filename(filename_str: str, raises_exception: bool):
	if raises_exception:
		with pytest.raises(BusinessRuleValidationException):
			Filename(filename_str)
	else:
		filename = Filename(filename_str)
		assert filename is not None


@pytest.mark.parametrize("size_bytes_val, raises_exception", [
	(-234, True),
	(0, True),
	(1, False),
	(10_000, False),
	(1_000_000_000_000, True)
])
def test_video_size_bytes(size_bytes_val: int, raises_exception: bool):
	if raises_exception:
		with pytest.raises(BusinessRuleValidationException):
			SizeBytes(size_bytes_val)
	else:
		size_bytes = SizeBytes(size_bytes_val)
		assert size_bytes is not None

@pytest.mark.parametrize("prev_status, new_status, method, raises_exception", [
	(VideoStatus.UPLOADED, VideoStatus.READY, video.mark_as_ready, False),
	(VideoStatus.UPLOADED, VideoStatus.FAILED, video.mark_as_failed, False),
	(VideoStatus.UPLOADED, VideoStatus.PROCESSING, video.start_processing, True),
	(VideoStatus.UPLOADED, VideoStatus.COMPLETED, video.complete_processing, True),
	(VideoStatus.READY, VideoStatus.PROCESSING, video.start_processing, False),
	(VideoStatus.READY, VideoStatus.FAILED, video.mark_as_failed, False),
	(VideoStatus.READY, VideoStatus.READY, video.mark_as_ready, True),
	(VideoStatus.READY, VideoStatus.COMPLETED, video.complete_processing, True),
	(VideoStatus.PROCESSING, VideoStatus.COMPLETED, video.complete_processing, False),
	(VideoStatus.PROCESSING, VideoStatus.FAILED, video.mark_as_failed, False),
	(VideoStatus.PROCESSING, VideoStatus.READY, video.mark_as_ready, True),
	(VideoStatus.PROCESSING, VideoStatus.PROCESSING, video.start_processing, True),
	(VideoStatus.COMPLETED, VideoStatus.READY, video.mark_as_ready, True),
	(VideoStatus.COMPLETED, VideoStatus.PROCESSING, video.start_processing, True),
	(VideoStatus.COMPLETED, VideoStatus.COMPLETED, video.complete_processing, True),
	(VideoStatus.COMPLETED, VideoStatus.FAILED, video.mark_as_failed, True),
	(VideoStatus.FAILED, VideoStatus.FAILED, video.mark_as_failed, True),
	(VideoStatus.FAILED, VideoStatus.READY, video.mark_as_ready, True),
	(VideoStatus.FAILED, VideoStatus.PROCESSING, video.start_processing, True),
	(VideoStatus.FAILED, VideoStatus.COMPLETED, video.complete_processing, True),
])
def test_video_status_transition(prev_status: VideoStatus, new_status: VideoStatus, method: Callable, raises_exception: bool):
	video.status = prev_status

	if raises_exception:
		with pytest.raises(InvalidVideoStateTransition):
			method()
	else:
		method()
		assert video.status == new_status