from pydantic import BaseModel
import uuid


class VideoSchema(BaseModel):
    id: uuid.UUID
    filename: str
    size_bytes: int
    status: str
