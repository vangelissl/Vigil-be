from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .video import VideoModel

from datetime import UTC, datetime

import uuid

from sqlalchemy import DateTime, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(256), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(
        String(256), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC))

    videos: Mapped[List["VideoModel"]] = relationship( # type: ignore
        back_populates="owner")  
