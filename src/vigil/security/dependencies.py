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
        authorization: Annotated[str | None, Header()] = None,
        service: TokenService = Depends(get_token_service)) -> CurrentUserDTO:
    """Returns the current user if they are logged, otherwise raises an exception"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
        user = service.decode_token(token)
    except:
        raise HTTPException(status_code=401, detail="Not logged in")

    return CurrentUserDTO(
        id=uuid.UUID(user.sub),
        username=user.username
    )


async def get_hasher():
    return PasswordHasher()