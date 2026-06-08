import uuid

from ..domain.entities import Analysis, AnalysisId, AnalysisStatus, UserId, VideoId
from ..domain.exceptions import AnalysisNotFoundError

from ...videos.application.service import VideoService
from ..ports import AnalysisRepositoryProtocol

from .exceptions import AnalysisAccessDeniedError

from ....workers.dependencies import Celery


class AnalysisService:
    def __init__(self, analysis_repo: AnalysisRepositoryProtocol, video_service: VideoService, celery: Celery):
        self.analysis_repo = analysis_repo
        self.video_service = video_service
        self.celery = celery

    async def trigger(self, video_id: uuid.UUID, current_user_id: uuid.UUID) -> Analysis:
        video = await self.video_service.get_by_id(video_id, current_user_id)

        analysis = Analysis(
            id=AnalysisId(uuid.uuid4()),
            owner_id=UserId(video.owner_id.value),
            video_id=VideoId(video_id),
            classification_result=None,
            status=AnalysisStatus.PENDING
        )

        await self.analysis_repo.create(analysis)
        self.celery.send_task('run_inference', args=[str(analysis.id.value)])

        return analysis


    async def get_by_id(self, id: uuid.UUID, current_user_id: uuid.UUID) -> Analysis:
        analysis = await self.analysis_repo.get(id)

        if not analysis:
            raise AnalysisNotFoundError()
        
        if analysis.owner_id.value != current_user_id:
            raise AnalysisAccessDeniedError()

        return analysis
    
    async def list_by_owner(self, owner_id: uuid.UUID) -> list[Analysis]:
        return await self.analysis_repo.get_all_by_owner(owner_id)
