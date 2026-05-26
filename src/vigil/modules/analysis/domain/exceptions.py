from ....shared.exceptions import BusinessRuleValidationException, BusinessRuleException

class NegativeScoreError(BusinessRuleValidationException):
	def __init__(self, message: str = "Analysis score cannot be negative"):
		super().__init__(message)

class ScoreGreaterThanOneError(BusinessRuleValidationException):
	def __init__(self, message: str = "Analysis score must be in [0,1] range"):
		super().__init__(message)

class InvalidAnalysisStateTransition(BusinessRuleException):
	def __init__(self, message: str = "Invalid analysis state transition"):
		super().__init__(message)