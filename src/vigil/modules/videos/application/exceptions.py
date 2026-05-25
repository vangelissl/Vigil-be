from ..domain.exceptions import InvalidFileError


class FilenameNoneOrEmptyError(InvalidFileError):
	def __init__(self, message: str = "Filename is none or empty"):
		super().__init__(message)

class SizeUnknownError(InvalidFileError):
	def __init__(self, message: str = "Video size is unknown"):
		super().__init__(message)

class FileAccessDeniedError(Exception):
	def __init__(self, message: str = "Access to file denied"):
		super().__init__(message)