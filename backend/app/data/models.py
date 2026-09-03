from enum import StrEnum, auto
from typing import Self

from flask_login import UserMixin
from sqlalchemy import (
    Column,
    ColumnExpressionArgument,
    Enum,
    ForeignKey,
    String,
    Table,
    select,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.errors import NotFoundError, ResourceExistsError

# Junction table of books and their authors (since there can be many to many)
book_authors = Table(
    "book_authors",
    db.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True),
    Column("author_id", ForeignKey("authors.id"), primary_key=True),
)


class CRUDMixin:
    """Generic CRUD methods mix-in.

    Wrappers around plain database calls, to keep database out of view layer.
    """

    @classmethod
    def get_one(cls, *criteria: ColumnExpressionArgument) -> Self:
        """Query for one object based on criteria.

        Raises:
            NotFoundError if there is none found.
        """
        obj = db.session.scalar(
            select(cls).
            where(*criteria)
        )  # fmt: skip
        if obj is None:
            raise NotFoundError(cls.__name__)
        return obj

    @classmethod
    def get_all(cls, *criteria: ColumnExpressionArgument) -> list[Self]:
        return list(db.session.scalars(
            select(cls).
            where(*criteria)
        ))  # fmt: skip

    @classmethod
    def get_by_id(cls, id: int) -> Self:
        """Lookup an obj by it's PK id.

        Raises:
            NotFoundError if the id isn't found.
        """
        if (obj := db.session.get(cls, id)) is None:
            raise NotFoundError("id", id)
        return obj

    @classmethod
    def delete_by_id(cls, id: int) -> None:
        """Delete an obj by it's PK id.

        Raises:
            NotFoundError if the id isn't found (could already have been deleted.)
        """
        if (obj := cls.get_by_id(id)) is None:
            raise NotFoundError("id", id)
        obj.delete()

    @classmethod
    def create(cls, **kwargs) -> Self:
        try:
            return cls(**kwargs)._save()
        except IntegrityError:
            db.session.rollback()
            raise ResourceExistsError(cls.__name__)

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs) -> Self:
        for f, v in kwargs.items():
            setattr(self, f, v)
        return self._save()

    def _save(self) -> Self:
        db.session.add(self)
        db.session.commit()
        return self


class FetchStatus(StrEnum):
    """An enum to store the results from external fetches to ensure we can properly proceed all subsiquent
    for the same query."""

    not_attempted = auto()
    unreachable = auto()
    timeout = auto()
    not_found = auto()
    http_error = auto()
    invalid_format = auto()
    ok = auto()


class Book(CRUDMixin, db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    pages: Mapped[int] = mapped_column(default=1, server_default="1")
    publish_date: Mapped[str | None]
    isbn: Mapped[str | None] = mapped_column(String(13), unique=True)
    fetch_status: Mapped[FetchStatus] = mapped_column(
        Enum(FetchStatus, native_enum=False, create_constraint=False, length=20),
        server_default=FetchStatus.not_attempted,
    )

    _authors: Mapped[list["Author"]] = relationship(secondary=book_authors, back_populates="books")

    @hybrid_property
    def authors(self) -> list["Author"]:
        return self._authors

    @authors.inplace.setter
    def _authors_setter(self, value: "str | list[str] | list[Author] | None") -> None:
        # Using a protected attribute, so we can create a setter and getter
        self._authors = Author.from_string(value)

    @classmethod
    def get_by_isbn(cls, isbn: str | None) -> "Book | None":
        if not (isbn := cls.normalize_isbn(isbn)):
            return None
        return db.session.scalar(
            select(cls).
            where(cls.isbn == isbn)
        )  # fmt: skip

    @staticmethod
    def normalize_isbn(raw: str | None) -> str | None:
        if raw is None:
            return None
        return raw.replace("-", "").replace(" ", "").upper() or None


class Author(CRUDMixin, db.Model):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    books: Mapped[list["Book"]] = relationship(
        secondary=book_authors,
        back_populates="_authors",
    )

    @classmethod
    def from_string(cls, raw: "str | list[str] | list[Author] | None") -> list["Author"]:
        if not raw:
            return []

        if isinstance(raw, str):
            names = raw.split(",")
        else:
            names = raw

        res = []
        for n in names:
            if obj := db.session.scalar(select(cls).filter_by(name=n.strip())) is None:
                obj = cls(name=n.strip())
                db.session.add(obj)
                db.session.flush()
            res.append(obj)

        return res


class Playlist(CRUDMixin, db.Model):
    """A playlist is a group of tracks."""

    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(255))

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User | None"] = relationship(back_populates="playlists")

    tracks: Mapped[list["Track"]] = relationship(back_populates="playlist")


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

    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id"))
    book_id: Mapped["Book | None"] = mapped_column(ForeignKey("books.id"))

    playlist: Mapped["Playlist"] = relationship(back_populates="tracks")
    book: Mapped["Book"] = relationship()

    def verify_track_owner(self, uid: int) -> bool:
        playlist = Playlist.get_by_id(self.playlist_id)
        if not playlist:
            return False

        return playlist.user_id == uid

    @classmethod
    def create(cls, **kwargs) -> Self:
        # verify playlist exists
        # verify ownership
        return super().create(**kwargs)


class User(CRUDMixin, UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password_hash: Mapped[str] = mapped_column(String(128))

    playlists: Mapped[list["Playlist"]] = relationship(back_populates="user")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
