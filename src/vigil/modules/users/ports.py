from abc import ABC, abstractmethod

import uuid

from .domain.entities import User


class UserRepositoryProtocol(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    @abstractmethod
    async def get(self, user_id: uuid.UUID) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    async def get_all(self, limit: int = 50, offset: int = 0) -> list[User]:
        pass

    @abstractmethod
    async def update(self, user_id: uuid.UUID, user: User):
        pass

    @abstractmethod
    async def delete(self, user_id: uuid.UUID) -> bool:
        pass