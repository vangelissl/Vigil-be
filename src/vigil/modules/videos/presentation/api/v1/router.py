import uuid

from fastapi import APIRouter, Depends, UploadFile

from ......security.dependencies import get_current_user, CurrentUserDTO

from ....dependencies import VideoService, get_video_service

from ...dto.response import VideoDTO


router = APIRouter()


@router.post("/videos/upload/", tags=["video"])
async def upload(
        file: UploadFile,
        video_service: VideoService = Depends(get_video_service),
        current_user: CurrentUserDTO = Depends(get_current_user)
) -> VideoDTO:
    owner_id = current_user.id
    video = await video_service.upload_video(file, owner_id)

    return VideoDTO(
        filename=video.filename.value,
        size_bytes=video.size_bytes.value,
        status=str(video.status)
    )


@router.get("/videos/", tags=["video"])
async def get_all(
        video_service: VideoService = Depends(get_video_service),
        current_user: CurrentUserDTO = Depends(get_current_user)
) -> list[VideoDTO]:
    owner_id = current_user.id
    videos = await video_service.list_by_owner(owner_id)

    return [VideoDTO(
        filename=v.filename.value,
        size_bytes=v.size_bytes.value,
        status=str(v.status))
        for v in videos]


@router.get("/videos/{video_id}", tags=["video"])
async def get(
    video_id: uuid.UUID,
    video_service: VideoService = Depends(get_video_service),
    current_user: CurrentUserDTO = Depends(get_current_user)
) -> VideoDTO:
    video = await video_service.get_by_id(video_id, current_user.id)

    return VideoDTO(
        filename=video.filename.value,
        size_bytes=video.size_bytes.value,
        status=str(video.status))
