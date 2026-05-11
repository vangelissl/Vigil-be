from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)

import jwt
import uuid
from datetime import datetime, UTC, timedelta
from dataclasses import dataclass
from typing import Any

from ..core.config import settings
from .exceptions import TokenExpiredError, TokenInvalidError, TokenMissingError

@dataclass
class TokenPayload:
    sub: str
    username: str | None = None
    iat: int | None = None
    jti: str | None = None
    exp: int | None = None
    type: str | None = None

    def to_dict(self):
        return {
            "sub": self.sub,
            "username": self.username,
            "iat": self.iat,
            "jti": self.jti,
            "exp": self.exp,
            "type": self.type
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]):
        sub = payload.get("sub")
        if sub is None:
            raise jwt.InvalidTokenError("Missing 'sub'")

        return cls(
            sub=sub,
            username=payload.get("username"),
            iat=payload.get("iat"),
            jti=payload.get("jti"),
            exp=payload.get("exp"),
            type=payload.get("type")
        )


class TokenService:
    def __init__(self):
        self.algorithm = "EdDSA"
        
        self.private_key = load_pem_private_key(
            settings.eddsa_private_key.encode(),
            password=None,
        )

        self.public_key = load_pem_public_key(
            settings.eddsa_public_key.encode(),
        )
        
        self.access_lifespan_min = settings.jwt_access_token_expire_minutes
        self.refresh_lifespan_d = settings.jwt_refresh_token_expire_days

    def _build_payload(self, payload: TokenPayload, delta: timedelta, token_type: str):
        now = datetime.now(UTC)

        return TokenPayload(
            sub=payload.sub,
            username=payload.username,
            iat=int(now.timestamp()),
            exp=int((now + delta).timestamp()),
            jti=str(uuid.uuid4()),
            type=token_type
        )

    def create_access_token(self, payload: TokenPayload) -> str:
        full_payload = self._build_payload(payload, timedelta(minutes=self.access_lifespan_min), "access")
        return jwt.encode(
            full_payload.to_dict(), 
            self.private_key,  # type: ignore
            algorithm=self.algorithm)

    def create_refresh_token(self, payload: TokenPayload) -> str:
        full_payload = self._build_payload(payload, timedelta(days=self.refresh_lifespan_d), "refresh")
        return jwt.encode(
            full_payload.to_dict(), 
            self.private_key,  # type: ignore
            algorithm=self.algorithm)

    def decode_token(self, token: str) -> TokenPayload:
        if len(token) == 0:
            raise TokenMissingError()
        try:
            payload = jwt.decode(
                token, 
                self.public_key,  # type: ignore
                algorithms=[self.algorithm])
            return TokenPayload.from_dict(payload)
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise TokenInvalidError()
    
    def decode_refresh_token(self, token: str) -> TokenPayload:
        payload = self.decode_token(token)

        if payload.type != "refresh":
            raise TokenInvalidError()
        
        return payload