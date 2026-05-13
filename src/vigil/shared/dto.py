from dataclasses import dataclass
import uuid


@dataclass
class CurrentUserDTO:
    id: uuid.UUID
    username: str | None