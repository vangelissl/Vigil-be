from pydantic import BaseModel
from datetime import datetime
import uuid

class AnalysisSchema(BaseModel):
    id: uuid.UUID
    video_id: uuid.UUID
    result: dict
    status: str
    completed_at: datetime | None
