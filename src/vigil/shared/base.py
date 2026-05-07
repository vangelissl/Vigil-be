from abc import ABC

from typing import Any


class ValueObject(ABC):
	"""Base class for domain value objects"""
	value: Any


class Entity(ABC):
	"""Base class for domain entities"""
	id: ValueObject