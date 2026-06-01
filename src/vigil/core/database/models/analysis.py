from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserModel
    from .video import VideoModel

from datetime import UTC, datetime

import uuid

from sqlalchemy import DateTime, UUID, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....modules.analysis.domain.value_objects import AnalysisStatus
from ..base import Base


class AnalysisModel(Base):
    __tablename__ = 'analyses'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)

    video_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("videos.id"))
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    classification_result: Mapped[dict] = mapped_column(JSON, nullable=True)
    status: Mapped[AnalysisStatus] = mapped_column(
        SAEnum(AnalysisStatus, name="analysisstatus"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True)

    owner: Mapped["UserModel"] = relationship(back_populates="analyses")
    video: Mapped["VideoModel"] = relationship(back_populates="analyses")
