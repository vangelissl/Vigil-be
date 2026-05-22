from ....shared.exceptions import BusinessRuleException


class VideoNotFound(BusinessRuleException):
	def __init__(self, message: str = "Video not found"):
		super().__init__(message)

class InvalidVideoStateTransition(BusinessRuleException):
	def __init__(self, message: str = "Invalid video state transition"):
		super().__init__(message)

class VideoAlreadyExists(BusinessRuleException):
	def __init__(self, message: str = "Video with this id already exists"):
		super().__init__(message)