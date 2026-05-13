import pytest
from unittest.mock import patch
from vigil.modules.auth.application.dto import TokenPairDTO
from vigil.modules.auth.domain.exceptions import ConfirmPasswordMismatchError, TokenRevokedError, InvalidCredentialsError
from vigil.security.exceptions import TokenExpiredError
from vigil.modules.users.domain.exceptions import UserNotFoundError, EmailAlreadyTakenError


# --- login ---

async def test_login_success(auth_service, user_repository_mock, token_service, hasher, domain_user, login_dto, redis):
    user_repository_mock.get_by_email.return_value = domain_user
    hasher.verify.return_value = True
    token_service.create_access_token.return_value = "access_token"
    token_service.create_refresh_token.return_value = "refresh_token"
    redis.get.return_value = False

    result = await auth_service.login(login_dto)

    assert isinstance(result, TokenPairDTO)
    assert result.access_token == "access_token"
    assert result.refresh_token == "refresh_token"


async def test_login_wrong_password(auth_service, user_repository_mock, hasher, domain_user, login_dto):
    user_repository_mock.get_by_email.return_value = domain_user
    hasher.verify.return_value = False

    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(login_dto)


async def test_login_user_not_found(auth_service, user_repository_mock, login_dto):
    user_repository_mock.get_by_email.side_effect = UserNotFoundError()

    with pytest.raises(UserNotFoundError):
        await auth_service.login(login_dto)


async def test_login_calls_get_by_email_with_correct_email(auth_service, user_repository_mock, hasher, domain_user, login_dto):
    user_repository_mock.get_by_email.return_value = domain_user
    hasher.verify.return_value = False

    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(login_dto)

    user_repository_mock.get_by_email.assert_called_once_with(login_dto.email)


async def test_login_verifies_password_against_stored_hash(auth_service, user_repository_mock, hasher, domain_user, login_dto):
    user_repository_mock.get_by_email.return_value = domain_user
    hasher.verify.return_value = True
    token_service_mock = auth_service.token_service
    token_service_mock.create_access_token.return_value = "access_token"
    token_service_mock.create_refresh_token.return_value = "refresh_token"

    await auth_service.login(login_dto)

    hasher.verify.assert_called_once_with(
        login_dto.password, domain_user.password_hash)


async def test_login_creates_access_and_refresh_tokens(auth_service, user_repository_mock, token_service, hasher, domain_user, login_dto):
    user_repository_mock.get_by_email.return_value = domain_user
    hasher.verify.return_value = True
    token_service.create_access_token.return_value = "access_token"
    token_service.create_refresh_token.return_value = "refresh_token"

    await auth_service.login(login_dto)

    token_service.create_access_token.assert_called_once()
    token_service.create_refresh_token.assert_called_once()


# --- register ---

async def test_register_success(auth_service, user_repository_mock, token_service, hasher, register_dto, domain_user):
    user_repository_mock.create.return_value = domain_user
    user_repository_mock.get_by_email.return_value = domain_user
    hasher.hash.return_value = "hashed_password"
    hasher.verify.return_value = True
    token_service.create_access_token.return_value = "access_token"
    token_service.create_refresh_token.return_value = "refresh_token"

    result = await auth_service.register(register_dto)

    assert isinstance(result, TokenPairDTO)
    assert result.access_token == "access_token"
    assert result.refresh_token == "refresh_token"


async def test_register_password_mismatch(auth_service, register_dto):
    register_dto.confirm_password = "different_password"

    with pytest.raises(ConfirmPasswordMismatchError):
        await auth_service.register(register_dto)


async def test_register_hashes_password(auth_service, user_repository_mock, token_service, hasher, register_dto, domain_user):
    user_repository_mock.create.return_value = domain_user
    user_repository_mock.get_by_email.return_value = domain_user
    hasher.hash.return_value = "hashed_password"
    hasher.verify.return_value = True
    token_service.create_access_token.return_value = "access_token"
    token_service.create_refresh_token.return_value = "refresh_token"

    await auth_service.register(register_dto)

    hasher.hash.assert_called_once_with(register_dto.password)


async def test_register_calls_repository_create(auth_service, user_repository_mock, token_service, hasher, register_dto, domain_user):
    user_repository_mock.create.return_value = domain_user
    user_repository_mock.get_by_email.return_value = domain_user
    hasher.hash.return_value = "hashed_password"
    hasher.verify.return_value = True
    token_service.create_access_token.return_value = "access_token"
    token_service.create_refresh_token.return_value = "refresh_token"

    await auth_service.register(register_dto)

    user_repository_mock.create.assert_called_once()


async def test_register_duplicate_email(auth_service, user_repository_mock, hasher, register_dto):
    hasher.hash.return_value = "hashed_password"
    user_repository_mock.create.side_effect = EmailAlreadyTakenError()

    with pytest.raises(EmailAlreadyTakenError):
        await auth_service.register(register_dto)


async def test_register_does_not_store_plain_password(auth_service, user_repository_mock, token_service, hasher, register_dto, domain_user):
    hasher.hash.return_value = "hashed_password"
    user_repository_mock.create.return_value = domain_user
    user_repository_mock.get_by_email.return_value = domain_user
    hasher.verify.return_value = True
    token_service.create_access_token.return_value = "access_token"
    token_service.create_refresh_token.return_value = "refresh_token"

    await auth_service.register(register_dto)

    created_user = user_repository_mock.create.call_args[0][0]
    assert created_user.password_hash != register_dto.password
    assert created_user.password_hash == "hashed_password"


# --- refresh_token ---

async def test_refresh_token_success(auth_service, token_service, refresh_payload, redis):
    token_service.decode_refresh_token.return_value = refresh_payload
    token_service.create_access_token.return_value = "new_access_token"
    token_service.create_refresh_token.return_value = "new_refresh_token"
    redis.get.return_value = None

    result = await auth_service.refresh_token("old_refresh_token")

    assert isinstance(result, TokenPairDTO)
    assert result.access_token == "new_access_token"
    assert result.refresh_token == "new_refresh_token"


async def test_refresh_token_revoked(auth_service, token_service, refresh_payload, redis):
    token_service.decode_refresh_token.return_value = refresh_payload
    redis.get.return_value = {}

    with pytest.raises(TokenRevokedError):
        await auth_service.refresh_token("revoked_refresh_token")


async def test_refresh_token_rotates(auth_service, token_service, refresh_payload, redis):
    token_service.decode_refresh_token.return_value = refresh_payload
    token_service.create_access_token.return_value = "new_access_token"
    token_service.create_refresh_token.return_value = "new_refresh_token"
    redis.get.return_value = None

    await auth_service.refresh_token("old_refresh_token")

    # old token must be revoked and new refresh token issued
    token_service.create_refresh_token.assert_called_once()


async def test_refresh_token_old_token_invalidated(auth_service, token_service, refresh_payload, redis):
    token_service.decode_refresh_token.return_value = refresh_payload
    token_service.create_access_token.return_value = "new_access_token"
    token_service.create_refresh_token.return_value = "new_refresh_token"
    redis.get.return_value = None

    with patch.object(auth_service, "_revoke") as mock_revoke:
        await auth_service.refresh_token("old_refresh_token")
        mock_revoke.assert_called_once_with(refresh_payload)


# --- verify_token ---

async def test_verify_token_success(auth_service, token_service, access_payload, redis):
    token_service.decode_token.return_value = access_payload
    redis.get.return_value = None

    result = await auth_service.verify_token("valid_token")

    assert result == access_payload.sub


async def test_verify_token_revoked(auth_service, token_service, access_payload):
    token_service.decode_token.return_value = access_payload

    with patch("json.load", return_value={access_payload.jti: access_payload.sub}):
        with pytest.raises(TokenRevokedError):
            await auth_service.verify_token("revoked_token")


# --- logout ---

async def test_logout_revokes_token(auth_service, token_service, access_payload):
    token_service.decode_token.return_value = access_payload

    with patch.object(auth_service, "_revoke") as mock_revoke:
        auth_service.revoke_token("valid_token")
        mock_revoke.assert_called_once_with(access_payload)


async def test_logout_expired_token_does_not_raise(auth_service, token_service):
    token_service.decode_token.side_effect = TokenExpiredError()

    try:
        auth_service.revoke_token("expired_token")
    except TokenExpiredError:
        pytest.fail("logout should not raise on expired token")
