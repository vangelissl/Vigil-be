from fastapi import Depends, Cookie, HTTPException

from typing import Annotated

from ..shared.dto import CurrentUserDTO
from .token import TokenService
from .hashing import PasswordHasher


async def get_token_service() -> TokenService:
    return TokenService()

async def get_current_user(
        refresh_token: Annotated[str | None, Cookie()],
        service: TokenService = Depends(get_token_service)) -> CurrentUserDTO:
	"""Returns the current user if they are logged, otherwise raises an exception"""
	if not refresh_token:
		raise HTTPException(status_code=401, detail="Not logged in")
	user = service.decode_refresh_token(refresh_token)
	
	return CurrentUserDTO(
		id=user.sub,
		username=user.username
	)

async def get_hasher():
	return PasswordHasher()