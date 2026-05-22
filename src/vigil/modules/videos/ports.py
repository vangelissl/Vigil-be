from abc import ABC, abstractmethod

import uuid

from .domain.entities import Video


class VideoRepositoryProtocol(ABC):
    @abstractmethod
    async def create(self, video: Video) -> Video:
        pass
    
    @abstractmethod
    async def get(self, video_id: uuid.UUID) -> Video | None:
        pass

    @abstractmethod
    async def get_all(self, limit: int = 50, offset: int = 0) -> list[Video]:
        pass

    @abstractmethod
    async def update(self, video_id: uuid.UUID, video: Video):
        pass

    @abstractmethod
    async def delete(self, video_id: uuid.UUID) -> bool:
        pass