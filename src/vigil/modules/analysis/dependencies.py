from fastapi import Depends

from ...core.database.session import AsyncSession, get_async_session

from .application.service import AnalysisService
from .infrastructure.repository import AnalysisRepository

from ..videos.dependencies import VideoService, get_video_service
from ...workers.dependencies import Celery, get_celery


async def get_analysis_repo(
		session: AsyncSession = Depends(get_async_session)
):
	return AnalysisRepository(session)

async def get_analysis_service(
		analysis_repo: AnalysisRepository = Depends(get_analysis_repo),
		video_service: VideoService = Depends(get_video_service),
		celery: Celery = Depends(get_celery)
):
	return AnalysisService(analysis_repo, video_service, celery)
	
