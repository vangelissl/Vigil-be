from ....shared.exceptions import BusinessRuleException, BusinessRuleValidationException


class VideoNotFound(BusinessRuleException):
    def __init__(self, message: str = "Video not found"):
        super().__init__(message)


class InvalidVideoStateTransition(BusinessRuleException):
    def __init__(self, message: str = "Invalid video state transition"):
        super().__init__(message)


class VideoAlreadyExists(BusinessRuleException):
    def __init__(self, message: str = "Video with this id already exists"):
        super().__init__(message)


class WrongFileExtensionError(BusinessRuleValidationException):
    def __init__(self, message: str = "Wrong video format"):
        super().__init__(message)


class VideoSizeTooBigError(BusinessRuleValidationException):
    def __init__(self, message: str = "Video size is too big"):
        super().__init__(message)


class VideoSizeTooSmallError(BusinessRuleValidationException):
    def __init__(self, message: str = "Video size is too small"):
        super().__init__(message)


class FileEmptyError(BusinessRuleValidationException):
    def __init__(self, message: str = "File is empty"):
        super().__init__(message)

class InvalidFileError(BusinessRuleException):
    def __init__(self, message: str = "File is invalid"):
        super().__init__(message)