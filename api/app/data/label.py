import logging
from typing import TYPE_CHECKING, Self

from sqlalchemy import Column, ForeignKey, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db
from app.data.base import CRUDMixin

if TYPE_CHECKING:
    from app.data.track import Track

logger = logging.getLogger(__name__)

track_labels = Table(
    "track_labels",
    db.metadata,
    Column("track_id", ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True),
    Column("label_id", ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True),
)


class Label(CRUDMixin, db.Model):
    __tablename__ = "labels"
    __table_args__ = (UniqueConstraint("user_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(50))

    tracks: Mapped[list["Track"]] = relationship(secondary=track_labels, back_populates="labels")

    @classmethod
    def get_all_owned(cls, user_id: int) -> list[Self]:
        return cls.get_all(cls.user_id == user_id)
