from vigil.modules.auth.dependencies import get_auth_service
from vigil.modules.users.dependencies import get_user_service
from vigil.core.dependencies import Redis
from vigil.modules.users.application.service import UserService
from vigil.modules.users.domain.value_objects import UserId, Email, Username
from vigil.modules.users.domain.entities import User
from vigil.modules.users.domain.exceptions import UserNotFoundError
from vigil.modules.users.ports import UserRepositoryProtocol
from vigil.modules.auth.domain.exceptions import ConfirmPasswordMismatchError, TokenRevokedError
from vigil.modules.auth.application.dto import LoginDTO, RegisterDTO, TokenPairDTO
from vigil.modules.auth.application.service import AuthService
from vigil.security.hashing import PasswordHasher
from vigil.security.token import TokenService, TokenPayload
from vigil.security.dependencies import get_current_user

from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import os
from dotenv import load_dotenv
import pytest
from httpx import AsyncClient, ASGITransport

from src.vigil.core.database.base import Base
from vigil.core.database.session import AsyncSession, get_async_session, create_async_engine
from src.vigil.modules.users.infrastructure.repository import UserRepository

from vigil.modules.videos.domain.entities import Video, VideoId, VideoStatus, SizeBytes, Filename
from vigil.modules.videos.infrastructure.repository import VideoRepository
from vigil.modules.videos.application.service import VideoService
from vigil.modules.videos.dependencies import get_video_repository, get_video_service
from vigil.main import app


load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test_db")


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


@pytest.fixture(scope="function")
def video_repository(session):
    repository = VideoRepository(session)
    yield repository
    repository = None


@pytest.fixture
async def owner(user_repository):
    user = User(
        id=UserId(uuid.uuid4()),
        email=Email("owner@example.com"),
        username=Username("owner"),
        password_hash="hashed"
    )
    await user_repository.create(user)
    return user


@pytest.fixture
def video(owner):
    return Video(
        id=VideoId(uuid.uuid4()),
        owner_id=owner.id,
        filename=Filename("file.avi"),
        size_bytes=SizeBytes(153),
        status=VideoStatus.UPLOADED,
        minio_path="uri"
    )


@pytest.fixture(scope="function")
async def client(session):
    app.dependency_overrides[get_async_session] = lambda: session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# --- value fixtures ---


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def username() -> str:
    return "testuser"


@pytest.fixture
def email() -> str:
    return "test@example.com"


@pytest.fixture
def domain_user(user_id, username, email) -> User:
    return User(
        id=UserId(user_id),
        email=Email(email),
        username=Username(username),
        password_hash="hashed_password",
    )


@pytest.fixture
def login_dto() -> LoginDTO:
    return LoginDTO(email="test@example.com", password="plainpassword")


@pytest.fixture
def register_dto(username, email) -> RegisterDTO:
    return RegisterDTO(
        email=email,
        username=username,
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
    redis = MagicMock()
    redis.get = AsyncMock()

    return redis


# --- service ---

@pytest.fixture
def auth_service(user_repository_mock, token_service, hasher, redis) -> AuthService:
    return AuthService(
        user_repository=user_repository_mock,
        token_service=token_service,
        hasher=hasher,
        redis=redis
    )


@pytest.fixture
def user_service(user_repository_mock, hasher) -> UserService:
    return UserService(
        user_repo=user_repository_mock,
        hasher=hasher
    )


@pytest.fixture
def fake_tokens():
    return TokenPairDTO(
        access_token="fake_access_token",
        refresh_token="fake_refresh_token"
    )


@pytest.fixture
def mock_auth_service(fake_tokens):
    service = MagicMock()
    service.register = AsyncMock(return_value=fake_tokens)
    service.login = AsyncMock(return_value=fake_tokens)
    service.refresh_token = AsyncMock(return_value=fake_tokens)
    service.logout = MagicMock()
    return service


@pytest.fixture
def client_with_mock_auth(client, mock_auth_service):
    from vigil.main import app
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    yield client
    app.dependency_overrides.pop(get_auth_service, None)


@pytest.fixture
def mock_user_service():
    service = MagicMock()
    service.get_current_user_profile = AsyncMock()
    service.update_current_user_profile = AsyncMock()
    return service


@pytest.fixture
def mock_current_user(user_id, username):
    from vigil.shared.dto import CurrentUserDTO
    return CurrentUserDTO(id=user_id, username=username)


@pytest.fixture
def client_with_user_service(client, mock_user_service, mock_current_user):
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    yield mock_user_service, client
    app.dependency_overrides.pop(get_user_service, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def mock_video_service():
    service = MagicMock()
    service.upload_video = AsyncMock()
    service.get_by_id = AsyncMock()
    service.list_by_owner = AsyncMock()
    return service

@pytest.fixture
def client_with_video_service(client, mock_video_service, mock_current_user):
    app.dependency_overrides[get_video_service] = lambda: mock_video_service
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    yield mock_video_service, client
    app.dependency_overrides.pop(get_video_service, None)
    app.dependency_overrides.pop(get_current_user, None)