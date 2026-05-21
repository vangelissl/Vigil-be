from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ..application.exceptions import WrongPasswordError, UnauthorizedUserError


def register_exception_handler(app: FastAPI):

    @app.exception_handler(UnauthorizedUserError)
    async def unauthorized_user_handler(request: Request, exc: UnauthorizedUserError):
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
