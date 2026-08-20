import enum
from typing import Self

from flask import url_for
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
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

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
    def get_one(cls, *criteria: ColumnExpressionArgument) -> Self | None:
        return db.session.scalar(
            select(cls).
            where(*criteria)
        )  # fmt: skip

    @classmethod
    def get_all(cls, *criteria: ColumnExpressionArgument) -> list[Self] | None:
        return list(db.session.scalars(
            select(cls).
            where(*criteria)
        ))  # fmt: skip

    @classmethod
    def get_by_id(cls, id: int | None) -> Self | None:
        if id is None:
            return None
        return db.session.get(cls, id)

    @classmethod
    def delete_by_id(cls, id: int | None) -> bool:
        if (obj := cls.get_by_id(id)) is None:
            return False
        obj.delete()
        return True

    @classmethod
    def create(cls, **kwargs) -> Self:
        return cls(**kwargs)._save()

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def _save(self) -> Self:
        db.session.add(self)
        db.session.commit()
        return self

    def to_json(self) -> dict[any]:
        raise NotImplementedError


class Book(CRUDMixin, db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    number_of_pages: Mapped[int] = mapped_column(default=1, server_default="1")
    publish_date: Mapped[str | None]
    isbn: Mapped[str | None] = mapped_column(String(13), unique=True)

    _authors: Mapped[list["Author"]] = relationship(
        secondary=book_authors, back_populates="books"
    )

    @hybrid_property
    def authors(self) -> list["Author"]:
        return self._authors

    @authors.inplace.setter
    def authors(self, value: "str | list[str] | list[Author] | None") -> None:
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

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "authors": [a.name for a in self.authors],
            "number_of_pages": self.number_of_pages,
            "publish_date": self.publish_date,
            "isbn": self.isbn,
            "cover_url": url_for(
                "api.books.get_book_cover", book_id=self.id, _external=True
            ),
        }


class Author(CRUDMixin, db.Model):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    books: Mapped[list["Book"]] = relationship(
        secondary=book_authors,
        back_populates="_authors",
    )

    @classmethod
    def from_string(cls, raw: str | list[str] | None) -> list["Author"]:
        if not raw:
            return []

        if isinstance(raw, str):
            names = raw.split(",")
        else:
            names = raw

        res = []
        for n in names:
            if (
                obj := db.session.scalar(select(cls).filter_by(name=n.strip()))
            ) is None:
                obj = cls(name=n.strip())
                db.session.add(obj)
                db.session.flush()
            res.append(obj)

        return res


class Playlist(CRUDMixin, db.Model):
    """A group of tracks."""

    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(255))

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User | None"] = relationship(back_populates="playlists")

    tracks: Mapped[list["Track"]] = relationship(back_populates="playlist")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "user_id": self.user_id,
        }  # fmt: skip


class Medium(enum.Enum):
    pdf = "pdf"
    oreilly = "oreilly"
    physical = "physical"
    audio = "audio"


class Track(CRUDMixin, db.Model):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    current_page: Mapped[int] = mapped_column(server_default="1")
    medium: Mapped[Medium | None] = mapped_column(Enum(Medium))

    playlist_id: Mapped[int | None] = mapped_column(ForeignKey("playlists.id"))
    book_id: Mapped["Book | None"] = mapped_column(ForeignKey("books.id"))

    playlist: Mapped["Playlist"] = relationship(back_populates="tracks")
    book: Mapped["Book"] = relationship()

    def to_json(self):
        return {
            "id": self.id,
            "current_page": self.current_page,
            "medium": self.medium.value if self.medium else None,
            "book_id": self.book_id,
        }


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

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
        }
