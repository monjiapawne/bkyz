import enum

from flask_login import UserMixin
from sqlalchemy import Column, Enum, ForeignKey, String, Table, select
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


class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    number_of_pages: Mapped[int] = mapped_column(server_default="0")
    publish_date: Mapped[str | None]
    isbn: Mapped[str | None] = mapped_column(String(13), unique=True)

    _authors: Mapped[list["Author"]] = relationship(secondary=book_authors, back_populates="books")

    @hybrid_property
    def authors(self) -> list["Author"]:
        return self._authors

    @authors.inplace.setter
    def authors(self, value: "str | list[str] | list[Author] | None") -> None:
        self._authors = Author.from_string(value)

    @classmethod
    def get_by_id(cls, book_id: int | None) -> "Book | None":
        if book_id is None:
            return None
        return db.session.get(cls, book_id)

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
        }


class Author(db.Model):
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

        return [get_or_create(cls, name=n.strip()) for n in names]


class Shelf(db.Model):
    __tablename__ = "shelves"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User | None"] = relationship(back_populates="shelves")

    shelf_books: Mapped[list["ShelfBook"]] = relationship(back_populates="shelf")


class Medium(enum.Enum):
    pdf = "pdf"
    oreilly = "oreilly"
    physical = "physical"
    audio = "audio"


class ShelfBook(db.Model):
    __tablename__ = "shelf_books"

    id: Mapped[int] = mapped_column(primary_key=True)
    current_page: Mapped[int] = mapped_column(server_default="1")
    medium: Mapped[Medium | None] = mapped_column(Enum(Medium))

    shelf_id: Mapped[int | None] = mapped_column(ForeignKey("shelves.id"))
    book_id: Mapped["Book | None"] = mapped_column(ForeignKey("books.id"))

    shelf: Mapped["Shelf"] = relationship(back_populates="shelf_books")
    book: Mapped["Book"] = relationship()

    @classmethod
    def get_by_book_id(cls, book_id: str) -> "ShelfBook | None":
        return db.session.scalar(
            select(cls)
            .where(cls.book_id == book_id)
        )  # fmt: skip


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password_hash: Mapped[str] = mapped_column(String(128))

    shelves: Mapped[list["Shelf"]] = relationship(back_populates="user")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_user(cls, username: str | None) -> "User | None":
        return db.session.scalar(select(cls).where(cls.username == username))  # no: fix

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
        }


def get_or_create[T](model: type[T], **filters) -> T:
    """Generic function to get and possibly create an object in the database

    Args:
        model: model type to search for
        filters: kwags to optionally filter to the query
    """
    obj = db.session.scalar(select(model).filter_by(**filters))
    if obj is None:
        obj = model(**filters)
        db.session.add(obj)
        db.session.flush()
    return obj
