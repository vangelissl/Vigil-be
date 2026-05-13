import pytest
import jwt

from vigil.security.token import TokenService
from vigil.security.exceptions import TokenExpiredError

service = TokenService()

def test_jwt_access_token_encode_decode(user_id, username):
    access_token = service.create_access_token(user_id, username)
    decoded_payload = service.decode_token(access_token)

    assert decoded_payload.type is not None and decoded_payload.type.lower() == "access"
    assert str(user_id) == decoded_payload.sub
    assert username == decoded_payload.username


def test_jwt_refresh_token_encode_decode(user_id, username):
    refresh_token = service.create_refresh_token(user_id, username)
    decoded_payload = service.decode_token(refresh_token)

    assert decoded_payload.type is not None and decoded_payload.type.lower() == "refresh"
    assert str(user_id) == decoded_payload.sub
    assert username == decoded_payload.username


def test_jwt_access_token_expired(user_id, username):
    service.access_lifespan_min = 0
    access_token = service.create_access_token(user_id, username)

    with pytest.raises(TokenExpiredError):
        decoded_payload = service.decode_token(access_token)
