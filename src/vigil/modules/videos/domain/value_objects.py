from dataclasses import dataclass

import uuid

from ....shared.base import ValueObject

from enum import Enum


@dataclass(frozen=True)
class VideoId(ValueObject):
	value: uuid.UUID


class VideoStatus(Enum):
	UPLOADED = 0
	READY = 1