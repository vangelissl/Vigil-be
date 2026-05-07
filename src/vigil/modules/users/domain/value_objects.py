from dataclasses import dataclass

import uuid

import re

from vigil.shared.base import ValueObject
from vigil.shared.exceptions import BusinessRuleValidationException


@dataclass(frozen=True)
class UserId(ValueObject):
	value: uuid.UUID


@dataclass(frozen=True)
class Email(ValueObject):
	value: str

	def __post_init__(self):
		pattern = (
            r"^(?!\.)(?!.*\.\.)[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"r"@[a-zA-Z0-9-]+\.[a-zA-Z]{2,256}$")
		
		if not re.match(pattern, self.value):
			raise BusinessRuleValidationException('email address is invalid')
		

@dataclass(frozen=True)
class Username(ValueObject):
    value: str

    def __post_init__(self):
        pattern = (r"^[A-Za-z0-9_]{5,256}$")

        if not re.match(pattern, self.value):
            raise BusinessRuleValidationException('username is invalid')