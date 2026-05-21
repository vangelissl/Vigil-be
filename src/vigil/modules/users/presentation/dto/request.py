from pydantic import BaseModel, EmailStr


class UpdateUserSchema(BaseModel):
	password: str
	email: EmailStr | None
	username: str | None
	new_password: str | None