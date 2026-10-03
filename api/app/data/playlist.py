import logging
from typing import TYPE_CHECKING, Self

from sqlalchemy import (
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db
from app.data.base import CRUDMixin, SortOrderMixin
from app.data.user import User
from app.errors import ForbiddenAsNotFound, NotFoundError

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.data.track import Track


class Playlist(SortOrderMixin, CRUDMixin, db.Model):
    """A playlist is a group of tracks."""

    __tablename__ = "playlists"
    __sort_scope__ = "user_id"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(255))

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User | None"] = relationship(back_populates="playlists")

    # Delete all tracks when a playlist is deleted
    tracks: Mapped[list["Track"]] = relationship(
        back_populates="playlist", cascade="all, delete-orphan", order_by="Track.sort_order"
    )

    @classmethod
    def get_owned(cls, playlist_id: int, user_id: int) -> Self:
        playlist = cls.get_by_id(playlist_id)
        if playlist is None:
            raise NotFoundError("playlist")
        if playlist.user_id != user_id:
            raise ForbiddenAsNotFound("playlist")

        return playlist
