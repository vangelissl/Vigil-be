from ....shared.exceptions import BusinessRuleException, BusinessRuleValidationException


class UserNotFoundError(BusinessRuleException):
	def __init__(self, message: str = "User not found"):
		super().__init__(message)


class UserAlreadyExistsError(BusinessRuleException):
	def __init__(self, message: str = "User already exists"):
		super().__init__(message)


class InvalidCredentialsError(BusinessRuleException):
	def __init__(self, message: str = "User not found"):
		super().__init__(message)


class EmailAlreadyTakenError(UserAlreadyExistsError):
	def __init__(self, message: str = "User with this email already exists"):
		super().__init__(message)


class UsernameAlreadyTakenError(UserAlreadyExistsError):
	def __init__(self, message: str = "User with this username already exists"):
		super().__init__(message)


class InvalidCredentialsFormatError(BusinessRuleValidationException):
    pass