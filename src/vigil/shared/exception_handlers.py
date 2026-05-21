from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse

from ..modules.users.domain.exceptions import UserNotFoundError, EmailAlreadyTakenError, UsernameAlreadyTakenError


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(EmailAlreadyTakenError)
    async def email_already_taken_handler(request: Request, exc: EmailAlreadyTakenError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "User with this email already exists"}
        )

    @app.exception_handler(UsernameAlreadyTakenError)
    async def username_already_taken_handler(request: Request, exc: UsernameAlreadyTakenError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "User with this username already exists"}
        )
    
    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request: Request, exc: UserNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "User not found"}
        )
    
	# --- fallback ---

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )