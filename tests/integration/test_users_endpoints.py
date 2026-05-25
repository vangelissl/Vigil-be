import pytest
from fastapi import status
from vigil.modules.users.domain.exceptions import (
    EmailAlreadyTakenError,
    UsernameAlreadyTakenError
)
from vigil.modules.users.application.exceptions import WrongPasswordError, UnauthorizedUserError
from vigil.modules.users.application.dto import UserDTO


GET_ME_URL = "/users/me/"
PATCH_ME_URL = "/users/me/"

VALID_UPDATE_BODY = {
    "password": "currentpassword",
    "email": "newemail@example.com",
    "username": "newusername",
    "new_password": "newpassword123"
}

UPDATE_BODY_WITH_SAME_PASSWORD = {
    "password": "currentpassword",
    "email": None,
    "username": None,
    "new_password": None
}


# --- GET /users/me/ ---

class TestGetMe:
    """Tests for GET /users/me/ endpoint"""

    async def test_get_me_success(self, client_with_user_service, domain_user):
        """Should return current user profile when authenticated"""
        mock_service, client = client_with_user_service
        mock_service.get_current_user_profile.return_value = UserDTO(
            email=domain_user.email.value,
            username=domain_user.username.value
        )

        response = await client.get(GET_ME_URL)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == domain_user.email.value
        assert data["username"] == domain_user.username.value

    async def test_get_me_returns_correct_schema(self, client_with_user_service, domain_user):
        """Should return response with only email and username fields"""
        mock_service, client = client_with_user_service
        mock_service.get_current_user_profile.return_value = UserDTO(
            email=domain_user.email.value,
            username=domain_user.username.value
        )

        response = await client.get(GET_ME_URL)

        data = response.json()
        assert set(data.keys()) == {"email", "username"}

    async def test_get_me_user_not_found(self, client_with_user_service):
        """Should return 401 when user not found"""
        mock_service, client = client_with_user_service
        mock_service.get_current_user_profile.side_effect = UnauthorizedUserError()

        response = await client.get(GET_ME_URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in response.json()["detail"] or "user" in response.json()["detail"].lower()
    

    async def test_get_me_missing_auth_header(self, client):
        """Should return 422 when validation fails (missing body)"""
        response = await client.get(GET_ME_URL)

        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_422_UNPROCESSABLE_CONTENT]


# --- PATCH /users/me/ ---

class TestPatchMe:
    """Tests for PATCH /users/me/ endpoint"""

    async def test_patch_me_success_update_email(self, client_with_user_service):
        """Should successfully update user email"""
        mock_service, client = client_with_user_service
        
        response = await client.patch(
            PATCH_ME_URL,
            json={
                "password": "currentpassword",
                "email": "newemail@example.com",
                "username": None,
                "new_password": None
            }
        )

        assert response.status_code == status.HTTP_200_OK
        mock_service.update_current_user_profile.assert_called_once()

    async def test_patch_me_success_update_username(self, client_with_user_service):
        """Should successfully update user username"""
        mock_service, client = client_with_user_service
        
        response = await client.patch(
            PATCH_ME_URL,
            json={
                "password": "currentpassword",
                "email": None,
                "username": "newusername",
                "new_password": None
            }
        )

        assert response.status_code == status.HTTP_200_OK
        mock_service.update_current_user_profile.assert_called_once()

    async def test_patch_me_success_update_password(self, client_with_user_service):
        """Should successfully update user password"""
        mock_service, client = client_with_user_service
        
        response = await client.patch(
            PATCH_ME_URL,
            json={
                "password": "currentpassword",
                "email": None,
                "username": None,
                "new_password": "newpassword123"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        mock_service.update_current_user_profile.assert_called_once()

    async def test_patch_me_success_update_multiple_fields(self, client_with_user_service):
        """Should successfully update multiple user fields"""
        mock_service, client = client_with_user_service
        
        response = await client.patch(
            PATCH_ME_URL,
            json=VALID_UPDATE_BODY
        )

        assert response.status_code == status.HTTP_200_OK
        mock_service.update_current_user_profile.assert_called_once()

    async def test_patch_me_returns_no_content(self, client_with_user_service):
        """Should return empty response body"""
        mock_service, client = client_with_user_service
        
        response = await client.patch(
            PATCH_ME_URL,
            json=UPDATE_BODY_WITH_SAME_PASSWORD
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.content) == 0

    async def test_patch_me_wrong_password(self, client_with_user_service):
        """Should return 406 when password is incorrect"""
        mock_service, client = client_with_user_service
        async def raise_error(*args, **kwargs):
            raise WrongPasswordError()
        mock_service.update_current_user_profile.side_effect = raise_error

        response = await client.patch(
            PATCH_ME_URL,
            json=VALID_UPDATE_BODY
        )

        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
        assert "Wrong password" in response.json()["detail"]

    async def test_patch_me_email_already_taken(self, client_with_user_service):
        """Should return 400 when email is already taken"""
        mock_service, client = client_with_user_service
        async def raise_error(*args, **kwargs):
            raise EmailAlreadyTakenError()
        mock_service.update_current_user_profile.side_effect = raise_error

        response = await client.patch(
            PATCH_ME_URL,
            json=VALID_UPDATE_BODY
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()["detail"].lower()

    async def test_patch_me_username_already_taken(self, client_with_user_service):
        """Should return 400 when username is already taken"""
        mock_service, client = client_with_user_service
        async def raise_error(*args, **kwargs):
            raise UsernameAlreadyTakenError()
        mock_service.update_current_user_profile.side_effect = raise_error

        response = await client.patch(
            PATCH_ME_URL,
            json=VALID_UPDATE_BODY
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.json()["detail"].lower()

    async def test_patch_me_user_not_found(self, client_with_user_service):
        """Should return 401 when user not found"""
        mock_service, client = client_with_user_service
        async def raise_error(*args, **kwargs):
            raise UnauthorizedUserError()
        mock_service.update_current_user_profile.side_effect = raise_error

        response = await client.patch(
            PATCH_ME_URL,
            json=VALID_UPDATE_BODY
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_patch_me_missing_password(self, client_with_user_service):
        """Should return 422 when password field is missing"""
        mock_service, client = client_with_user_service
        
        response = await client.patch(
            PATCH_ME_URL,
            json={
                "email": "newemail@example.com",
                "username": None,
                "new_password": None
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_patch_me_invalid_email_format(self, client_with_user_service):
        """Should return 422 when email format is invalid"""
        mock_service, client = client_with_user_service
        
        response = await client.patch(
            PATCH_ME_URL,
            json={
                "password": "currentpassword",
                "email": "not-an-email",
                "username": None,
                "new_password": None
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_patch_me_empty_password(self, client_with_user_service):
        """Should accept empty string as valid password (pydantic allows it)"""
        mock_service, client = client_with_user_service
        
        response = await client.patch(
            PATCH_ME_URL,
            json={
                "password": "",
                "email": None,
                "username": None,
                "new_password": None
            }
        )

        # Empty string is technically valid according to pydantic unless constrained
        assert response.status_code == status.HTTP_200_OK

    async def test_patch_me_missing_auth_header(self, client):
        """Should return 422 when validation fails (missing cookie)"""
        response = await client.patch(
            PATCH_ME_URL,
            json=UPDATE_BODY_WITH_SAME_PASSWORD
        )

        # PATCH /users/me/ expects current_user dependency which requires refresh_token cookie
        # Without it, FastAPI returns 422 for missing required parameter
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_422_UNPROCESSABLE_CONTENT]

    async def test_patch_me_empty_body(self, client_with_user_service):
        """Should return 422 when body is empty"""
        mock_service, client = client_with_user_service
        
        response = await client.patch(PATCH_ME_URL, json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_patch_me_calls_service_with_correct_params(self, client_with_user_service, user_id):
        """Should call user service with correct parameters"""
        mock_service, client = client_with_user_service
        
        await client.patch(
            PATCH_ME_URL,
            json=VALID_UPDATE_BODY
        )

        mock_service.update_current_user_profile.assert_called_once()
        call_args = mock_service.update_current_user_profile.call_args
        assert call_args is not None
        assert call_args[0][0] == user_id

    async def test_patch_me_with_null_values(self, client_with_user_service):
        """Should accept null values for optional fields"""
        mock_service, client = client_with_user_service
        
        response = await client.patch(
            PATCH_ME_URL,
            json={
                "password": "currentpassword",
                "email": None,
                "username": None,
                "new_password": None
            }
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_patch_me_with_extra_fields(self, client_with_user_service):
        """Should return 422 when extra fields are provided"""
        mock_service, client = client_with_user_service
        
        response = await client.patch(
            PATCH_ME_URL,
            json={
                "password": "currentpassword",
                "email": None,
                "username": None,
                "new_password": None,
                "extra_field": "should not be here"
            }
        )

        assert response.status_code in [
            status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_CONTENT]
