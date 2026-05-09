from dataclasses import dataclass


@dataclass
class CurrentUserDTO:
    id: str
    username: str | None