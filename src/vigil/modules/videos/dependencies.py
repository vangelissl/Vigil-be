from fastapi import Depends

from ...core.database.session import AsyncSession, get_async_session
from ...core.dependencies import MinioStorage, get_minio_storage

from .infrastructure.repository import VideoRepository
from .application.service import VideoService


async def get_video_repository(
    session: AsyncSession = Depends(get_async_session)
):
    return VideoRepository(session)


async def get_video_service(
        video_repository: VideoRepository = Depends(get_video_repository),
        minio_storge: MinioStorage = Depends(get_minio_storage)
):
    return VideoService(video_repository, minio_storge)