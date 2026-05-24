from dataclasses import dataclass

from pathlib import Path
import uuid

from ....shared.base import ValueObject

from .exceptions import FileEmptyError, WrongFileExtensionError, FileTooLargeError, FileTooSmallError

from enum import Enum


@dataclass(frozen=True)
class VideoId(ValueObject):
    value: uuid.UUID


class VideoStatus(Enum):
    UPLOADED = "uploaded"
    READY = "ready"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov"}


@dataclass(frozen=True)
class Filename(ValueObject):
    value: str

    def __post_init__(self):
        if not self.value:
            raise FileEmptyError("Filename cannot be empty")
        ext = Path(self.value).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise WrongFileExtensionError(
                f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")


@dataclass(frozen=True)
class SizeBytes(ValueObject):
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise FileTooSmallError("File size is too small")
        elif self.value > 1_000_000_000:
            raise FileTooLargeError(
                "File size is too big. It must be <= 1GB")
