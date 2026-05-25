from fastapi import Depends, Header, HTTPException

import jwt

from typing import Annotated

import uuid

from ..shared.dto import CurrentUserDTO
from .token import TokenService
from .hashing import PasswordHasher


async def get_token_service() -> TokenService:
    return TokenService()


async def get_current_user(
        access_token: Annotated[str | None, Header()],
        service: TokenService = Depends(get_token_service)) -> CurrentUserDTO:
    """Returns the current user if they are logged, otherwise raises an exception"""
    if not access_token:
        raise HTTPException(status_code=401, detail="Not logged in")
    try:
        user = service.decode_token(access_token)
    except:
        raise HTTPException(status_code=401, detail="Not logged in")

    return CurrentUserDTO(
        id=uuid.UUID(user.sub),
        username=user.username
    )


async def get_hasher():
    return PasswordHasher()