import pytest
import jwt

from vigil.security.token import TokenPayload, TokenService

service = TokenService()
payload = TokenPayload(
    sub="user_id",
    username="user9283492"
)


def test_jwt_access_token_encode_decode():
    access_token = service.create_access_token(payload)
    decoded_payload = service.decode_token(access_token)

    assert decoded_payload.type is not None and decoded_payload.type.lower() == "access"
    assert payload.sub == decoded_payload.sub
    assert payload.username == decoded_payload.username


def test_jwt_refresh_token_encode_decode():
    refresh_token = service.create_refresh_token(payload)
    decoded_payload = service.decode_token(refresh_token)

    assert decoded_payload.type is not None and decoded_payload.type.lower() == "refresh"
    assert payload.sub == decoded_payload.sub
    assert payload.username == decoded_payload.username


def test_jwt_access_token_expired():
    service.access_lifespan_min = 0
    access_token = service.create_access_token(payload)

    with pytest.raises(jwt.InvalidTokenError):
        decoded_payload = service.decode_token(access_token)
