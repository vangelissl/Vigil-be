from fastapi import Depends

from ...core.database.session import AsyncSession, get_async_session
from .infrastructure.repository import UserRepository


async def get_user_repository(
	session: AsyncSession = Depends(get_async_session)
) -> UserRepository:
	return UserRepository(session)