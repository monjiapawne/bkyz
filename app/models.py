import enum

from sqlalchemy import Column, Enum, ForeignKey, Table, select, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

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

    authors: Mapped[list["Author"]] = relationship(secondary=book_authors, back_populates="books")

    @staticmethod
    def normalize_isbn(raw: str | None) -> str | None:
        if raw is None:
            return None
        return raw.replace("-", "").replace(" ", "").upper() or None

    @validates("isbn")
    def _validate_isbn(self, key: str, value: str | None) -> str | None:
        return self.normalize_isbn(value)

    def to_dict(self):
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
        back_populates="authors",
    )


class Shelf(db.Model):
    __tablename__ = "shelves"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User | None"] = relationship(back_populates="shelves")

    shelf_books: Mapped[list["ShelfBook"]] = relationship(back_populates="shelf")


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    shelves: Mapped[list["Shelf"]] = relationship(back_populates="user")


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


def get_or_create[T](model: type[T], **filters) -> T:
    obj = db.session.scalar(select(model).filter_by(**filters))
    if obj is None:
        obj = model(**filters)
        db.session.add(obj)
        db.session.flush()
    return obj
