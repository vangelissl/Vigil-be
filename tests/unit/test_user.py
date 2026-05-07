import pytest
import uuid

from src.vigil.shared.exceptions import BusinessRuleValidationException
from src.vigil.modules.users.domain.value_objects import Email, UserId, Username
from src.vigil.modules.users.domain.entities import User


@pytest.mark.parametrize("email_str, raises_exception", [
    ("invald_email", True),
    ("valid@gmail.com", False),
    ("", True),
])
def test_user_email(email_str: str, raises_exception: bool):
    if raises_exception:
        with pytest.raises(BusinessRuleValidationException):
            Email(email_str)
    else:
        email = Email(email_str)
        assert email is not None


@pytest.mark.parametrize("username_str, raises_exception",[
    ("invalid_username%", True),
    ("user_234234", False),
    ("987987582735", False),
    ("vary_long_username" * 200, True)
])
def test_user_username(username_str: str, raises_exception: bool):
    if raises_exception:
        with pytest.raises(BusinessRuleValidationException):
            Username(username_str)
    else:
        username = Username(username_str)
        assert username is not None



def test_user_create():
    userId = UserId(uuid.uuid4())
    email = Email("test@gmail.com")
    username = Username("user92348")
    password_hash = "kkjsda;lfjds;l"

    user = User(userId, email, username, password_hash)

    assert user is not None