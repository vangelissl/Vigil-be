from fastapi import UploadFile

import uuid

from ....core.dependencies import MinioStorage

from ..ports import VideoRepositoryProtocol

from .exceptions import FilenameNoneOrEmptyError, SizeUnknownError
from ..domain.entities import Video, VideoId, VideoStatus, Filename, SizeBytes, UserId
from ..domain.exceptions import VideoNotFound


class VideoService:

	def __init__(self, video_repository: VideoRepositoryProtocol, storage: MinioStorage):
		self.video_repository = video_repository
		self.storage = storage

	async def upload_video(self, file: UploadFile, owner_id: uuid.UUID) -> Video:
		minio_path = await self.storage.upload(file)

		if not file.filename:
			raise FilenameNoneOrEmptyError()
		
		if not file.size:
			raise SizeUnknownError()

		video = Video(
			id=VideoId(uuid.uuid4()),
			owner_id=UserId(owner_id),
			filename=Filename(file.filename),
			size_bytes=SizeBytes(file.size),
			status=VideoStatus.UPLOADED,
			minio_path=minio_path
		)

		created_video = await self.video_repository.create(video)

		return created_video

	async def get_by_id(self, id: uuid.UUID):
		video = await self.video_repository.get(id)

		if not video:
			raise VideoNotFound()
		
		return video
	
	async def list_by_owner(self, owner_id: uuid.UUID):
		videos = await self.video_repository.get_all_by_owner(owner_id)

		return videos