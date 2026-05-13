from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from slowapi.errors import RateLimitExceeded

from ..domain.exceptions import ConfirmPasswordMismatchError, InvalidCredentialsError, TokenRevokedError

from ...users.domain.exceptions import EmailAlreadyTakenError, UsernameAlreadyTakenError, UserAlreadyExistsError, UserNotFoundError

from ....security.exceptions import TokenInvalidError, TokenExpiredError


def register_exception_handlers(app: FastAPI) -> None:

    # --- register ---

    @app.exception_handler(ConfirmPasswordMismatchError)
    async def confirm_password_mismatch_handler(request: Request, exc: ConfirmPasswordMismatchError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": "Passwords do not match"}
        )

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

    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "User with at least one of these credentials already exists"}
        )

    # --- login ---

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request: Request, exc: UserNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials"}
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials"}
        )
    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded", "limit": str(exc.detail)}
        )

    # --- token ---

    @app.exception_handler(TokenExpiredError)
    async def token_expired_handler(request: Request, exc: TokenExpiredError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token has expired"}
        )

    @app.exception_handler(TokenRevokedError)
    async def token_revoked_handler(request: Request, exc: TokenRevokedError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token has been revoked"}
        )

    @app.exception_handler(TokenInvalidError)
    async def token_invalid_handler(request: Request, exc: TokenInvalidError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token is invalid"}
        )

    # --- fallback ---

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )