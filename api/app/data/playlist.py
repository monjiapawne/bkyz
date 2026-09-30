import logging
from typing import TYPE_CHECKING, Self

from sqlalchemy import (
    ForeignKey,
    String,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db
from app.data.base import CRUDMixin
from app.data.user import User
from app.errors import NotFoundError

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.data.track import Track

class Playlist(CRUDMixin, db.Model):
    """A playlist is a group of tracks."""

    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(255))

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User | None"] = relationship(back_populates="playlists")

    # Delete all tracks when a playlist is deleted
    tracks: Mapped[list["Track"]] = relationship(
        back_populates="playlist", cascade="all, delete-orphan", order_by="Track.playlist_position"
    )

    @classmethod
    def get_owned(cls, playlist_id: int, user_id: int) -> Self:
        playlist = db.session.scalar(
            select(cls).where(cls.id == playlist_id, cls.user_id == user_id)
        )
        if playlist is None:
            logger.info(f"invalid resource access: user: {user_id} tried to access {playlist_id}")
            raise NotFoundError("playlist")

        return playlist