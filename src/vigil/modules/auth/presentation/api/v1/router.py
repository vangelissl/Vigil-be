from fastapi import APIRouter, Depends, Cookie, Response, HTTPException, status, Header

from typing import Annotated

from fastapi.responses import JSONResponse

from ....dependencies import AuthService, get_auth_service
from ....application.dto import LoginDTO, RegisterDTO, TokenPairDTO

from ...dto.request import LoginSchema, RegisterSchema


router = APIRouter()


@router.post("/auth/register/", tags=["auth"])
async def register(
    body: RegisterSchema,
    auth: AuthService = Depends(get_auth_service)
) -> Response:
    model = RegisterDTO(
        email=body.email,
        username=body.username,
        password=body.password,
        confirm_password=body.confirm_password
    )
    tokens = await auth.register(model)
    return _response_with_tokens_set(tokens)


@router.post("/auth/login/", tags=["auth"])
async def login(
        body: LoginSchema,
        auth: AuthService = Depends(get_auth_service)
) -> Response:
    model = LoginDTO(
        body.email,
        body.password
    )
    tokens = await auth.login(model)
    return _response_with_tokens_set(tokens)


@router.post("/auth/refresh/", tags=["auth"])
async def refresh(
    refresh_token: Annotated[str | None, Cookie()] = None,
    auth: AuthService = Depends(get_auth_service)
) -> Response:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    tokens = await auth.refresh_token(refresh_token)
    return _response_with_tokens_set(tokens)


@router.post("/auth/logout/", tags=["auth"])
async def logout(
    refresh_token: Annotated[str | None, Cookie()] = None,
    access_token: Annotated[str | None, Header()] = None,
    auth: AuthService = Depends(get_auth_service)
):
    if not refresh_token or not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    
    tokens = TokenPairDTO(access_token, refresh_token)
    auth.logout(tokens)

    return Response(status_code=status.HTTP_200_OK)


def _response_with_tokens_set(pair: TokenPairDTO) -> Response:
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"access_token": pair.access_token}
    )
    response.set_cookie(
        key="refresh_token",
        value=pair.refresh_token,
        httponly=True,
        samesite="strict",
        secure=True
    )
    return response