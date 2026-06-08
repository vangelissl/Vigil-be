from fastapi import APIRouter, Depends

import uuid

from ......security.dependencies import get_current_user, CurrentUserDTO

from ....dependencies import AnalysisService, get_analysis_service

from ...dto.response import AnalysisSchema

router = APIRouter()


@router.get("/analyses", tags=["analyses"])
async def list_all(
    current_user: CurrentUserDTO = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> list[AnalysisSchema]:
    analyses = await analysis_service.list_by_owner(current_user.id)
    
    return [AnalysisSchema(
        id=analysis.id.value,
        video_id=analysis.video_id.value,
        result=analysis.classification_result.to_dict() if analysis.classification_result else {},
        status=analysis.status.value,
        completed_at=analysis.completed_at if analysis.completed_at else None
    ) for analysis in analyses]


@router.post("/videos/{video_id}/analyses", tags=["analyses"])
async def trigger(
        video_id: uuid.UUID,
        current_user: CurrentUserDTO = Depends(get_current_user),
        analysis_service: AnalysisService = Depends(get_analysis_service)
) -> AnalysisSchema:
    analysis = await analysis_service.trigger(video_id, current_user.id)

    return AnalysisSchema(
        id=analysis.id.value,
        video_id=analysis.video_id.value,
        result=analysis.classification_result.to_dict() if analysis.classification_result else {},
        status=analysis.status.value,  # ← Use .value instead of str()
        completed_at=analysis.completed_at if analysis.completed_at else None
    )


@router.get("/analyses/{analysis_id}", tags=["analyses"])
async def get(
    analysis_id: uuid.UUID,
    current_user: CurrentUserDTO = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> AnalysisSchema:
    analysis = await analysis_service.get_by_id(analysis_id, current_user.id)
    
    print(f"DEBUG: analysis.classification_result = {analysis.classification_result}")
    print(f"DEBUG: analysis.status = {analysis.status}")
    
    result_dict = analysis.classification_result.to_dict() if analysis.classification_result else {}
    print(f"DEBUG: result_dict = {result_dict}")
    
    return AnalysisSchema(
        id=analysis.id.value,
        video_id=analysis.video_id.value,
        result=result_dict,
        status=analysis.status.value,
        completed_at=analysis.completed_at if analysis.completed_at else None
    )