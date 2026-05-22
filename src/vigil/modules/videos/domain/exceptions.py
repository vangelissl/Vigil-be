from ....shared.exceptions import BusinessRuleException


class VideoNotFound(BusinessRuleException):
	def __init__(self, message: str = "Video not found"):
		super().__init__(message)