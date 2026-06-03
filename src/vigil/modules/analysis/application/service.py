import uuid

from ..domain.entities import Analysis, AnalysisId, AnalysisStatus, UserId, VideoId
from ..domain.exceptions import AnalysisNotFoundError

from ...videos.application.service import VideoService
from ..ports import AnalysisRepositoryProtocol

from vigil_tasks.analysis import run_inference

from .exceptions import AnalysisAccessDeniedError


class AnalysisService:
    def __init__(self, analysis_repo: AnalysisRepositoryProtocol, video_service: VideoService):
        self.analysis_repo = analysis_repo
        self.video_service = video_service

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
        run_inference.delay(str(analysis.id.value)) # type: ignore

        return analysis


    async def get_by_id(self, id: uuid.UUID, current_user_id: uuid.UUID) -> Analysis:
        analysis = await self.analysis_repo.get(id)

        if not analysis:
            raise AnalysisNotFoundError()
        
        if analysis.owner_id != current_user_id:
            raise AnalysisAccessDeniedError()

        return analysis
