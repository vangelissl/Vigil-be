class WrongPasswordError(Exception):
	def __init__(self, message: str = "Wrong password. Try again."):
		super().__init__(message)