from vigil.shared.exceptions import DomainException

class TokenError(DomainException):
    pass

class TokenInvalidError(TokenError):
	def __init__(self, message: str = "Token is invalid"):
		super().__init__(message)

class TokenExpiredError(TokenError):
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)

class TokenMissingError(TokenError):
	def __init__(self, message: str = "Token is missing"):
		super().__init__(message)