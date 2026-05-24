from pydantic import BaseModel


class VideoDTO(BaseModel):
	filename: str
	size_bytes: int
	status: str