import pytest
import uuid

from vigil.modules.videos.domain.entities import Video, UserId
from vigil.modules.videos.domain.value_objects import VideoId, VideoStatus, SizeBytes, Filename
from vigil.modules.videos.domain.exceptions import FileAlreadyExists


async def test_video_create(video_repository, video):
    await video_repository.create(video)

    created_video = await video_repository.get(video.id.value)

    assert created_video is not None
    assert created_video.id.value == video.id.value
    assert created_video.owner_id.value == video.owner_id.value
    assert created_video.filename.value == video.filename.value
    assert created_video.size_bytes.value == video.size_bytes.value
    assert created_video.status == video.status
    assert created_video.minio_path == video.minio_path


async def test_same_video_create(video_repository, video):
    _ = await video_repository.create(video)

    with pytest.raises(FileAlreadyExists):
        _ = await video_repository.create(video)


async def test_video_delete(video_repository, video):
    created_video = await video_repository.create(video)
    result = await video_repository.delete(created_video.id.value)

    assert result == True


async def test_non_existent_video_get(video_repository, video):
    video = await video_repository.get(uuid.uuid4())

    assert video is None


async def test_get_all_by_owner(video_repository, video):
    _ = await video_repository.create(video)

    videos = await video_repository.get_all_by_owner(video.owner_id.value)

    assert videos is not None
    assert len(videos) == 1
    assert videos[0].id.value == video.id.value


async def test_get_all(video_repository, video):
    _ = await video_repository.create(video)

    videos = await video_repository.get_all()

    assert videos is not None
    found_video = next((v for v in videos if v.id.value == video.id.value))
    assert found_video is not None


async def test_video_update(video_repository, video):
    created_video = await video_repository.create(video)

    created_video.mark_as_ready()
    await video_repository.update(created_video.id.value, created_video)
    updated_video = await video_repository.get(created_video.id.value)

    assert updated_video is not None
    assert updated_video.status == VideoStatus.READY
