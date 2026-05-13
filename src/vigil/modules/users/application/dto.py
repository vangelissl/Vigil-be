from dataclasses import dataclass 
import uuid 


@dataclass
class UserDTO:
	email: str
	username: str

@dataclass
class UpdateUserDTO:
	password: str 
	email: str | None = None
	username: str | None = None
	new_password: str | None = None