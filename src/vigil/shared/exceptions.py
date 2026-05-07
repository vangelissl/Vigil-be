class DomainException(Exception):
	pass


class BusinessRuleException(DomainException):
	pass


class BusinessRuleValidationException(DomainException):
	pass