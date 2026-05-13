from pydantic import BaseModel, EmailStr


class LoginSchema(BaseModel):
	email: EmailStr
	password: str


class RegisterSchema(BaseModel):
	email: EmailStr
	username: str
	password: str
	confirm_password: str