from fastapi import Depends

from .application.service import AuthService

from ..users.ports import UserRepositoryProtocol
from ..users.dependencies import get_user_repository

from ...security.dependencies import TokenService, get_token_service, PasswordHasher, get_hasher

from ...core.dependencies import get_redis, Redis


async def get_auth_service(
        user_repository: UserRepositoryProtocol = Depends(get_user_repository),
        token_service: TokenService = Depends(get_token_service),
        hasher: PasswordHasher = Depends(get_hasher),
        redis: Redis = Depends(get_redis),
) -> AuthService:
    return AuthService(user_repository, token_service, hasher, redis)