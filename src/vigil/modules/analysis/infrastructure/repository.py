import uuid

from sqlalchemy import select

from ..ports import AnalysisRepositoryProtocol

from ....core.database.session import AsyncSession
from ....core.database.models.analysis import AnalysisModel

from ..domain.entities import Analysis, AnalysisId, AnalysisStatus, UserId, VideoId, ClassificationResult
from ..domain.exceptions import AnalysisNotFoundError


class AnalysisRepository(AnalysisRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    def _to_model(self, analysis: Analysis) -> AnalysisModel:
        return AnalysisModel(
            id=analysis.id.value,
            video_id=analysis.video_id.value,
            owner_id=analysis.owner_id.value,
            classification_result=analysis.classification_result.to_dict(
            ) if analysis.classification_result else None,
            status=analysis.status,
            created_at=analysis.created_at,
            completed_at=analysis.completed_at
        )

    def _to_domain(self, model: AnalysisModel) -> Analysis:
        return Analysis(
            id=AnalysisId(model.id),
            owner_id=UserId(model.owner_id),
            status=AnalysisStatus(model.status),
            video_id=VideoId(model.video_id),
            classification_result=ClassificationResult.from_dict(
                model.classification_result) if model.classification_result else None,
            created_at=model.created_at,
            completed_at=model.completed_at
        )

    async def get(self, analysis_id: uuid.UUID) -> Analysis | None:
        model = await self.session.get(AnalysisModel, analysis_id)
        return self._to_domain(model) if model else None

    async def create(self, analysis: Analysis) -> Analysis:
        model = self._to_model(analysis)
        self.session.add(model)
        await self.session.flush()
        return analysis

    async def delete(self, analysis_id: uuid.UUID) -> bool:
        analysis = await self.session.get(AnalysisModel, analysis_id)

        if not analysis:
            return False

        await self.session.delete(analysis)
        await self.session.flush()

        return True

    async def get_all_by_owner(self, owner_id: uuid.UUID) -> list[Analysis]:
        analysis_models = (await self.session.execute(select(AnalysisModel).where(AnalysisModel.owner_id == owner_id))).scalars()

        return [self._to_domain(model) for model in analysis_models]
    
    async def update(self, analysis: Analysis):
        model = await self.session.get(AnalysisModel, analysis.id.value)

        if not model:
            raise AnalysisNotFoundError()
        
        model.id = analysis.id.value
        model.owner_id = analysis.owner_id.value
        model.video_id = analysis.video_id.value
        model.status = analysis.status
        
        if analysis.classification_result:
            model.classification_result["predicted_class"] = analysis.classification_result.predicted_class
            model.classification_result["confidence"] = analysis.classification_result.confidence
            model.classification_result["all_scores"] = analysis.classification_result.all_scores
        
        model.completed_at = analysis.completed_at