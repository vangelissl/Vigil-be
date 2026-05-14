from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ..domain.exceptions import UserNotFoundError, EmailAlreadyTakenError, UsernameAlreadyTakenError
from ..application.exceptions import WrongPasswordError


def register_exception_handler(app: FastAPI):

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request: Request, exc: UserNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Unauthorized user. Access denied"}
        )

    @app.exception_handler(WrongPasswordError)
    async def wrong_password_handler(request: Request, exc: WrongPasswordError):
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={"detail": "Wrong password. Action denied"}
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
