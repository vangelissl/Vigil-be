import uuid

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..ports import VideoRepositoryProtocol

from ..domain.exceptions import FileNotFound, FileAlreadyExists
from ..domain.value_objects import VideoId, Filename, SizeBytes
from ..domain.entities import Video, UserId

from vigil.core.database.models.video import VideoModel


class VideoRepository(VideoRepositoryProtocol):

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, video: VideoModel) -> Video:
        return Video(
            id=VideoId(video.id),
            owner_id=UserId(video.owner_id),
            filename=Filename(video.filename),
            status=video.status,
            size_bytes=SizeBytes(video.size_bytes),
            minio_path=video.minio_path
        )

    def _to_model(self, video: Video) -> VideoModel:
        return VideoModel(
            id=video.id.value,
            owner_id=video.owner_id.value,
            filename=video.filename.value,
            minio_path=video.minio_path,
            status=video.status,
            size_bytes=video.size_bytes.value
        )

    async def create(self, video: Video) -> Video:
        existing_video = (await self.session.execute(
            select(VideoModel)
            .where(or_(
                VideoModel.id == video.id.value,
            ))
        )).scalar()

        if not existing_video:
            model = self._to_model(video)
            self.session.add(model)
            await self.session.flush()
            return self._to_domain(model)
        else:
            raise FileAlreadyExists()

    async def get(self, video_id: uuid.UUID) -> Video | None:
        video = await self.session.get(VideoModel, video_id)

        return self._to_domain(video) if video else None

    async def get_all_by_owner(self, owner_id: uuid.UUID) -> list[Video]:
        models = (await self.session.scalars(
            select(VideoModel).where(VideoModel.owner_id == owner_id)
        )).all()

        return [self._to_domain(m) for m in models]

    async def get_all(self, limit: int = 50, offset: int = 0) -> list[Video]:
        models = (await self.session.scalars(
            select(VideoModel).limit(limit).offset(offset)
        )).all()

        return [self._to_domain(m) for m in models]

    async def update(self, video_id: uuid.UUID, video: Video):
        video_to_update = await self.session.get(VideoModel, video_id)

        if not video_to_update:
            raise FileNotFound("user not found")
        video_to_update.filename = video.filename.value
        video_to_update.minio_path = video.minio_path
        video_to_update.owner_id = video.owner_id.value
        video_to_update.size_bytes = video.size_bytes.value
        video_to_update.status = video.status

        await self.session.flush()

    async def delete(self, video_id: uuid.UUID) -> bool:
        video_to_delete = await self.session.get(VideoModel, video_id)

        if not video_to_delete:
            return False

        await self.session.delete(video_to_delete)
        await self.session.flush()

        return True
