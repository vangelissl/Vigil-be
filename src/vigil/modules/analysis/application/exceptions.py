class AnalysisAccessDeniedError(Exception):
	def __init__(self, message: str = "Analysis access denied"):
		super().__init__(message)