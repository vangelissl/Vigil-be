from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ..domain.exceptions import ConfirmPasswordMismatchError, InvalidCredentialsError, TokenRevokedError

from ...users.domain.exceptions import UserAlreadyExistsError

from ....security.exceptions import TokenInvalidError, TokenExpiredError


def register_exception_handlers(app: FastAPI) -> None:

    # --- register ---

    @app.exception_handler(ConfirmPasswordMismatchError)
    async def confirm_password_mismatch_handler(request: Request, exc: ConfirmPasswordMismatchError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": "Passwords do not match"}
        )

    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "User with at least one of these credentials already exists"}
        )

    # --- login ---

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials"}
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