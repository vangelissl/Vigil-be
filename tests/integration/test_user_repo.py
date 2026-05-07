import pytest
import uuid
from src.vigil.modules.users.domain.entities import User
from src.vigil.modules.users.domain.exceptions import UserAlreadyExistsError, UserNotFoundError, EmailAlreadyTakenError,  UsernameAlreadyTakenError
from src.vigil.modules.users.domain.value_objects import UserId, Email, Username

user = User(
    id=UserId(uuid.uuid4()),
    email=Email("test1@example.com"),
    username=Username("user23984"),
    password_hash="lkasjdfljdf"
)

user_same_id = User(
    id=UserId(user.id.value),
    email=Email("test4@example.com"),
    username=Username("user23587592"),
    password_hash="kjsdlgjslgjsl"
)

user_same_email = User(
    id=UserId(uuid.uuid4()),
    email=Email(user.email.value),
    username=Username("user23424"),
    password_hash="lskjdfljfljf"
)

user_same_username = User(
    id=UserId(uuid.uuid4()),
    email=Email("test3@example.com"),
    username=Username(user.username.value),
    password_hash="kasjdflkjfljfls"
)


async def test_user_create(user_repository):
    await user_repository.create(user)

    created_user = await user_repository.get(user.id.value)
    print(created_user.username)

    assert created_user is not None
    assert created_user.username.value == user.username.value


@pytest.mark.parametrize("other_user, exception", [
    (user_same_id, UserAlreadyExistsError),
    (user_same_email, EmailAlreadyTakenError),
    (user_same_username, UsernameAlreadyTakenError)
]
)
async def test_same_user_create(user_repository, other_user, exception):
    created_user = await user_repository.create(user)

    with pytest.raises(exception):
        await user_repository.create(other_user)


async def test_user_delete(user_repository):
    created_user = await user_repository.create(user)
    result = await user_repository.delete(created_user.id.value)

    assert result == True


async def test_non_existing_user_get(user_repository):
    with pytest.raises(UserNotFoundError):
        await user_repository.get(uuid.uuid4())


async def test_user_get_by_email(user_repository):
    _ = await user_repository.create(user)

    created_user = await user_repository.get_by_email(user.email.value)

    assert created_user is not None
    assert created_user.id.value == user.id.value


async def test_user_get_by_username(user_repository):
    _ = await user_repository.create(user)

    created_user = await user_repository.get_by_username(user.username.value)

    assert created_user is not None
    assert created_user.id.value == user.id.value
