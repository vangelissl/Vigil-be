import os
from datetime import datetime, UTC
from dotenv import load_dotenv
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from src.vigil.core.database.base import Base
from src.vigil.modules.users.infrastructure.repository import UserRepository


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test_db")


@pytest.fixture(scope="function")
async def engine():
	engine = create_async_engine(DATABASE_URL)
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
		yield engine
		await engine.dispose()


@pytest.fixture(scope="function")
async def session(engine):
	async with engine.connect() as conn:
		await conn.begin()
		await conn.begin_nested()
		async with AsyncSession(bind=conn) as s:
			yield s
		await conn.rollback()

@pytest.fixture(scope="function")
def user_repository(session):
	repository = UserRepository(session)

	yield repository

	repository = None

import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from vigil.security.token import TokenService, TokenPayload
from vigil.security.hashing import PasswordHasher

from vigil.modules.auth.application.service import AuthService
from vigil.modules.auth.application.dto import LoginDTO, RegisterDTO, TokenPairDTO
from vigil.modules.auth.domain.exceptions import ConfirmPasswordMismatchError, TokenRevokedError

from vigil.modules.users.ports import UserRepositoryProtocol
from vigil.modules.users.domain.exceptions import UserNotFoundError
from vigil.modules.users.domain.entities import User
from vigil.modules.users.domain.value_objects import UserId, Email, Username

from vigil.core.dependencies import Redis

# --- value fixtures ---

@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()

@pytest.fixture
def username() -> str:
     return "testuser"


@pytest.fixture
def domain_user(user_id) -> User:
    return User(
        id=UserId(user_id),
        email=Email("test@example.com"),
        username=Username("testuser"),
        password_hash="hashed_password",
    )


@pytest.fixture
def login_dto() -> LoginDTO:
    return LoginDTO(email="test@example.com", password="plainpassword")


@pytest.fixture
def register_dto() -> RegisterDTO:
    return RegisterDTO(
        email="test@example.com",
        username="testuser",
        password="plainpassword",
        confirm_password="plainpassword"
    )


@pytest.fixture
def access_payload(user_id, username) -> TokenPayload:
    return TokenPayload(
        sub=str(user_id),
        username=username,
        jti=str(uuid.uuid4()),
        iat=0,
        exp=0,
        type="access"
    )


@pytest.fixture
def refresh_payload(user_id, username) -> TokenPayload:
    return TokenPayload(
        sub=str(user_id),
        username=username,
        jti=str(uuid.uuid4()),
        iat=0,
        exp=0,
        type="refresh"
    )


# --- mock dependencies ---

@pytest.fixture
def user_repository_mock() -> AsyncMock:
    return AsyncMock(spec=UserRepositoryProtocol)


@pytest.fixture
def token_service() -> MagicMock:
    return MagicMock(spec=TokenService)


@pytest.fixture
def hasher() -> MagicMock:
    return MagicMock(spec=PasswordHasher)

@pytest.fixture
def redis() -> MagicMock:
     return MagicMock(spec=Redis)


# --- service ---

@pytest.fixture
def auth_service(user_repository_mock, token_service, hasher, redis) -> AuthService:
    return AuthService(
        user_repository=user_repository_mock,
        token_service=token_service,
        hasher=hasher,
        redis=redis
    )