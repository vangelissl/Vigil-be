from ....shared.exceptions import BusinessRuleException, BusinessRuleValidationException


class FileNotFound(BusinessRuleException):
    def __init__(self, message: str = "File not found"):
        super().__init__(message)


class FileAlreadyExists(BusinessRuleException):
    def __init__(self, message: str = "File with this id already exists"):
        super().__init__(message)

# --- Invalid File ---

class InvalidFileError(BusinessRuleValidationException):
    def __init__(self, message: str = "File is invalid"):
        super().__init__(message)


class WrongFileExtensionError(InvalidFileError):
    def __init__(self, message: str = "Wrong file format"):
        super().__init__(message)


class FileTooLargeError(InvalidFileError):
    def __init__(self, message: str = "File size is too big"):
        super().__init__(message)


class FileTooSmallError(InvalidFileError):
    def __init__(self, message: str = "File size is too small"):
        super().__init__(message)


class FileEmptyError(InvalidFileError):
    def __init__(self, message: str = "File is empty"):
        super().__init__(message)

# --- Invalid Behavior ---

class InvalidVideoStateTransition(BusinessRuleException):
    def __init__(self, message: str = "Invalid video state transition"):
        super().__init__(message)