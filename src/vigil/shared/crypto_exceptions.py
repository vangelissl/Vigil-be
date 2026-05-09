import jwt

class TokenExpiredError(jwt.ExpiredSignatureError):
	def __init__(self, message: str = "Token has expired"):
		super().__init__(message)
	

class TokenInvalidError(jwt.InvalidTokenError):
	def __init__(self, message: str = "Token is invalid"):
		super().__init__(message)
	

class TokenMissingError(jwt.InvalidTokenError):
	def __init__(self, message: str = "Token is missing"):
		super().__init__(message)