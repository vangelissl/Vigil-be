import pytest
from fastapi import status

from vigil.modules.auth.domain.exceptions import ConfirmPasswordMismatchError, TokenRevokedError
from vigil.modules.users.domain.exceptions import (
    UserNotFoundError,
    EmailAlreadyTakenError,
    UsernameAlreadyTakenError
)

REGISTER_URL = "/auth/register/"
LOGIN_URL = "/auth/login/"
REFRESH_URL = "/auth/refresh/"
LOGOUT_URL = "/auth/logout/"

VALID_REGISTER_BODY = {
    "email": "test@example.com",
    "phone_number": "+1234567890",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "password": "pass123",
    "confirm_password": "pass123"
}

VALID_LOGIN_BODY = {
    "email": "test@example.com",
    "password": "pass123"
}


# --- register ---

async def test_register_success(client_with_mock_auth, mock_auth_service, fake_tokens):
    mock_auth_service.register.return_value = fake_tokens

    response = await client_with_mock_auth.post(REGISTER_URL, json=VALID_REGISTER_BODY)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["access_token"] == "fake_access_token"


async def test_register_sets_refresh_token_cookie(client_with_mock_auth, mock_auth_service, fake_tokens):
    mock_auth_service.register.return_value = fake_tokens

    response = await client_with_mock_auth.post(REGISTER_URL, json=VALID_REGISTER_BODY)

    assert "refresh_token" in response.cookies


async def test_register_email_already_taken(client_with_mock_auth, mock_auth_service):
    mock_auth_service.register.side_effect = EmailAlreadyTakenError()

    response = await client_with_mock_auth.post(REGISTER_URL, json=VALID_REGISTER_BODY)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.json()["detail"].lower()


async def test_register_username_already_taken(client_with_mock_auth, mock_auth_service):
    mock_auth_service.register.side_effect = UsernameAlreadyTakenError()

    response = await client_with_mock_auth.post(REGISTER_URL, json=VALID_REGISTER_BODY)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.json()["detail"].lower()


async def test_register_password_mismatch(client_with_mock_auth, mock_auth_service):
    mock_auth_service.register.side_effect = ConfirmPasswordMismatchError()

    body = {**VALID_REGISTER_BODY, "confirm_password": "different"}
    response = await client_with_mock_auth.post(REGISTER_URL, json=body)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_register_missing_required_fields(client_with_mock_auth):
    response = await client_with_mock_auth.post(REGISTER_URL, json={"email": "test@example.com"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_register_invalid_email_format(client_with_mock_auth):
    body = {**VALID_REGISTER_BODY, "email": "not_an_email"}
    response = await client_with_mock_auth.post(REGISTER_URL, json=body)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# --- login ---

async def test_login_success(client_with_mock_auth, mock_auth_service, fake_tokens):
    mock_auth_service.login.return_value = fake_tokens

    response = await client_with_mock_auth.post(LOGIN_URL, json=VALID_LOGIN_BODY)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["access_token"] == "fake_access_token"


async def test_login_sets_refresh_token_cookie(client_with_mock_auth, mock_auth_service, fake_tokens):
    mock_auth_service.login.return_value = fake_tokens

    response = await client_with_mock_auth.post(LOGIN_URL, json=VALID_LOGIN_BODY)

    assert "refresh_token" in response.cookies


async def test_login_invalid_credentials(client_with_mock_auth, mock_auth_service):
    mock_auth_service.login.side_effect = UserNotFoundError()

    response = await client_with_mock_auth.post(LOGIN_URL, json=VALID_LOGIN_BODY)

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_login_missing_email(client_with_mock_auth):
    response = await client_with_mock_auth.post(LOGIN_URL, json={"password": "pass123"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_login_missing_password(client_with_mock_auth):
    response = await client_with_mock_auth.post(LOGIN_URL, json={"email": "test@example.com"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_login_empty_body(client_with_mock_auth):
    response = await client_with_mock_auth.post(LOGIN_URL, json={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# --- refresh ---

async def test_refresh_success(client_with_mock_auth, mock_auth_service, fake_tokens):
    mock_auth_service.refresh_token.return_value = fake_tokens

    client_with_mock_auth.cookies.set("refresh_token", "valid_refresh_token")

    response = await client_with_mock_auth.post(REFRESH_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["access_token"] == "fake_access_token"


async def test_refresh_sets_new_cookie(client_with_mock_auth, mock_auth_service, fake_tokens):
    mock_auth_service.refresh_token.return_value = fake_tokens

    client_with_mock_auth.cookies.set("refresh_token", "valid_refresh_token")
    response = await client_with_mock_auth.post(REFRESH_URL)

    assert "refresh_token" in response.cookies


async def test_refresh_missing_cookie(client_with_mock_auth):
    response = await client_with_mock_auth.post(REFRESH_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_refresh_revoked_token(client_with_mock_auth, mock_auth_service):
    mock_auth_service.refresh_token.side_effect = TokenRevokedError()

    client_with_mock_auth.cookies.set("refresh_token", "valid_refresh_token")

    response = await client_with_mock_auth.post(
        LOGOUT_URL,
        headers={"refresh-token": "valid_access_token"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# --- logout ---

async def test_logout_success(client_with_mock_auth, mock_auth_service):
    client_with_mock_auth.cookies.set("refresh_token", "valid_refresh_token")

    response = await client_with_mock_auth.post(
        LOGOUT_URL,
        headers={"access-token": "valid_access_token"}
    )

    assert response.status_code == status.HTTP_200_OK


async def test_logout_missing_refresh_token(client_with_mock_auth):
    response = await client_with_mock_auth.post(
        LOGOUT_URL,
        headers={"access-token": "valid_access_token"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_logout_missing_access_token(client_with_mock_auth):
    client_with_mock_auth.cookies.set("refresh_token", "valid_refresh_token")

    response = await client_with_mock_auth.post(
        LOGOUT_URL,
        headers={"access-token": ""}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_logout_calls_service(client_with_mock_auth, mock_auth_service):
    client_with_mock_auth.cookies.set("refresh_token", "valid_refresh_token")

    await client_with_mock_auth.post(
        LOGOUT_URL,
        headers={"access-token": "valid_access_token"}
    )

    mock_auth_service.logout.assert_called_once()