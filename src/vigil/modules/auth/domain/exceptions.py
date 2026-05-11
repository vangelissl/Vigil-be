from ....shared.exceptions import DomainException, BusinessRuleException

from ....security.exceptions import TokenError


class ConfirmPasswordMismatchError(DomainException):
    def __init__(self):
        super().__init__("Confirm password does not match password")


class TokenRevokedError(TokenError):
	def __init__(self, message: str = "Token is revoked"):
		super().__init__(message)


class InvalidCredentialsError(BusinessRuleException):
	def __init__(self, message: str = "User not found"):
		super().__init__(message)