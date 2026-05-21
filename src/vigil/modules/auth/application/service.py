import uuid
from datetime import datetime, UTC

from .dto import LoginDTO, RegisterDTO, TokenPairDTO
from ..domain.exceptions import TokenRevokedError, ConfirmPasswordMismatchError, InvalidCredentialsError

from ....security.exceptions import TokenExpiredError
from ....security.token import TokenService, TokenPayload
from ....security.hashing import PasswordHasher

from ...users.ports import UserRepositoryProtocol
from ...users.domain.entities import User
from ...users.domain.value_objects import UserId, Email, Username
from ...users.domain.exceptions import UserNotFoundError

from ....core.dependencies import Redis


class AuthService:
    def __init__(self, user_repository: UserRepositoryProtocol, token_service: TokenService, hasher: PasswordHasher, redis: Redis):
        self.user_repository = user_repository
        self.token_service = token_service
        self.hasher = hasher
        self.redis = redis

    async def _is_revoked(self, payload: TokenPayload) -> bool:
        jti = payload.jti
        return await self.redis.get(jti) is not None

    def _revoke(self, payload: TokenPayload):
        now = datetime.now(UTC)
        expire_time = datetime.fromtimestamp(payload.exp, tz=UTC) 
        ttl = expire_time - now
        self.redis.set(payload.jti, payload.sub, ex=int(ttl.total_seconds()))
        

    def revoke_token(self, token: str):
        try:
            payload = self.token_service.decode_token(token)
            self._revoke(payload)
        except TokenExpiredError:
            pass

    async def login(self, user: LoginDTO) -> TokenPairDTO:
        found_user = await self.user_repository.get_by_email(user.email)

        if not found_user:
            raise UserNotFoundError()

        if not self.hasher.verify(
                user.password, found_user.password_hash):
            raise InvalidCredentialsError()

        access_token = self.token_service.create_access_token(found_user.id.value, found_user.username.value)
        refresh_token = self.token_service.create_refresh_token(
            found_user.id.value, found_user.username.value)

        return TokenPairDTO(
            access_token,
            refresh_token
        )

    async def refresh_token(self, refresh_token: str) -> TokenPairDTO:
        refresh_payload = self.token_service.decode_refresh_token(
            refresh_token)

        if await self._is_revoked(refresh_payload):
            raise TokenRevokedError()

        self._revoke(refresh_payload)

        new_access = self.token_service.create_access_token(uuid.UUID(refresh_payload.sub), refresh_payload.username)
        new_refresh = self.token_service.create_refresh_token(uuid.UUID(refresh_payload.sub), refresh_payload.username)

        return TokenPairDTO(new_access, new_refresh)

    async def register(self, user: RegisterDTO) -> TokenPairDTO:
        if user.password != user.confirm_password:
            raise ConfirmPasswordMismatchError()

        user_to_register = User(
            id=UserId(uuid.uuid4()),
            email=Email(user.email),
            username=Username(user.username),
            password_hash=self.hasher.hash(user.password),
        )

        await self.user_repository.create(user_to_register)
        return await self.login(LoginDTO(user.email, user.password))


    async def verify_token(self, token: str):
        payload = self.token_service.decode_token(token)

        if await self._is_revoked(payload):
            raise TokenRevokedError()

        return payload.sub

    def logout(self, pair: TokenPairDTO):
        self.revoke_token(pair.access_token)
        self.revoke_token(pair.refresh_token)