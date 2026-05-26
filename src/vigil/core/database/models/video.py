from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .user import UserModel
    from .analysis import AnalysisModel

from datetime import UTC, datetime

import uuid

from sqlalchemy import DateTime, String, UUID, ForeignKey, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....modules.videos.domain.value_objects import VideoStatus
from ..base import Base


class VideoModel(Base):
    __tablename__ = 'videos'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    filename: Mapped[str] = mapped_column(
        String(260), unique=False, nullable=False)
    minio_path: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[VideoStatus] = mapped_column(
        SAEnum(VideoStatus, name="videostatus"),
        nullable=False
    )
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC))

    owner: Mapped["UserModel"] = relationship(
        back_populates="videos")
    analyses: Mapped[List["AnalysisModel"]
                     ] = relationship(back_populates="video")
