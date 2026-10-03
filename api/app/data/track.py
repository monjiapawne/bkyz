import datetime
import logging
from enum import StrEnum, auto
from typing import Self

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    String,
    func,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db
from app.data.base import CRUDMixin
from app.data.book import Book
from app.data.playlist import Playlist
from app.errors import NotFoundError

logger = logging.getLogger(__name__)


class Medium(StrEnum):
    pdf = auto()
    physical = auto()
    audio = auto()
    ebook = auto()


class Track(CRUDMixin, db.Model):
    """A user book's copy of a book storing all their data, referencing a parent book."""

    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(server_default="1")
    unit: Mapped[str | None] = mapped_column(String(30), default=None)
    total: Mapped[int | None] = mapped_column(default=None)
    medium: Mapped[Medium] = mapped_column(Enum(Medium), server_default=Medium.physical.name)
    playlist_position: Mapped[int]
    active: Mapped[bool] = mapped_column(default=True)
    notes: Mapped[str | None] = mapped_column(default=None)
    rating: Mapped[int | None] = mapped_column(
        CheckConstraint("rating BETWEEN 1 AND 10", name="rating_range"), default=None
    )

    position_updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id", ondelete="CASCADE"))
    playlist: Mapped["Playlist"] = relationship(back_populates="tracks")

    book_id: Mapped[int | None] = mapped_column(ForeignKey("books.id"))
    book: Mapped["Book"] = relationship()

    progress_log: Mapped[list["TrackProgress"]] = relationship(
        back_populates="track", cascade="all, delete-orphan"
    )

    def progress_track(self, new_position: int):
        new_position = max(1, new_position)
        # Guard to > total
        if self.total is not None:
            new_position = min(self.total, new_position)

        # Avoid spamming log if there's no change
        old = self.position
        if old == new_position:
            return self

        self.position = new_position
        self.position_updated_at = func.now()
        db.session.add(
            TrackProgress(
                track_id=self.id,
                user_id=self.playlist.user_id,
                from_position=old,
                to_position=new_position,
                delta=new_position - old,
            )
        )
        db.session.commit()
        return self

    @classmethod
    def get_owned(cls, track_id: int, uid: int) -> Self:
        track = db.session.scalar(
            select(cls).join(Playlist).where(cls.id == track_id, Playlist.user_id == uid)
        )
        if track is None:
            raise NotFoundError("track")
        return track

    @classmethod
    def create(cls, playlist_id: int, **kwargs) -> Self:
        kwargs["playlist_id"] = playlist_id
        kwargs["playlist_position"] = cls._next_position(playlist_id)
        return super().create(**kwargs)

    @classmethod
    def _next_position(cls, playlist_id: int) -> int:
        """Calculates the next position for a track in a playlist"""
        return db.session.execute(
            select(func.coalesce(func.max(cls.playlist_position), 0) + 1).where(
                cls.playlist_id == playlist_id
            )
        ).scalar_one()


class TrackProgress(CRUDMixin, db.Model):
    """Append only log of position changes on a track."""

    __tablename__ = "track_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    from_position: Mapped[int]
    to_position: Mapped[int]
    delta: Mapped[int]
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    track: Mapped["Track"] = relationship(back_populates="progress_log")

    # TODO: add indexing for user_id and track_id for speed
