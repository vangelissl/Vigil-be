from pydantic import BaseModel, EmailStr


class UserProfileSchema(BaseModel):
	email: EmailStr
	username: str