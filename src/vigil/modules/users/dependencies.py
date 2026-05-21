from fastapi import Depends

from ...core.database.session import AsyncSession, get_async_session
from ...security.dependencies import PasswordHasher, get_hasher

from .infrastructure.repository import UserRepository

from .application.service import UserService


async def get_user_repository(
	session: AsyncSession = Depends(get_async_session)
) -> UserRepository:
	return UserRepository(session)


async def get_user_service(
		user_repo: UserRepository = Depends(get_user_repository),
		hasher: PasswordHasher = Depends(get_hasher)
) -> UserService:
	return UserService(user_repo, hasher)