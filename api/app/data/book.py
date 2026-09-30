from enum import StrEnum, auto
from typing import TYPE_CHECKING

from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    String,
    Table,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db
from app.data.base import CRUDMixin

if TYPE_CHECKING:
    from app.data.user import User


class FetchStatus(StrEnum):
    """An enum to store the results from external fetches to ensure we can
    properly proceed all subsiquent for the same query."""

    not_attempted = auto()
    unreachable = auto()
    timeout = auto()
    not_found = auto()
    http_error = auto()
    invalid_format = auto()
    unknown = auto()
    ok = auto()


# Junction table of books and their authors (since there can be many to many)
book_authors = Table(
    "book_authors",
    db.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True),
    Column("author_id", ForeignKey("authors.id"), primary_key=True),
)


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

    added_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    added_by: Mapped["User | None"] = relationship()

    _authors: Mapped[list["Author"]] = relationship(secondary=book_authors, back_populates="books")

    @property
    def authors(self) -> list["Author"]:
        return self._authors

    @authors.setter
    def authors(self, value: "str | list[str] | None") -> None:
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
    def from_string(cls, authors_raw: "str | list[str] | None") -> list["Author"]:
        """Takes a raw string or list of strings and converts them into a list of author objects.

        Checks if the authors already exist, if not it will create them.
        """
        if not authors_raw:
            return []

        # split the list of authors into a list
        names = authors_raw.split(",") if isinstance(authors_raw, str) else authors_raw

        authors = []
        for name in names:
            name = name.strip()
            # Check if the author already exists
            author = db.session.scalar(select(cls).filter_by(name=name))

            if author:
                # Author already exists, add it to the list
                authors.append(author)
                continue

            # If not we'll create a new author
            author = cls(name=name)
            db.session.add(author)
            db.session.flush()
            authors.append(author)

        return authors
