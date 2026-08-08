from sqlalchemy import Column, ForeignKey, Table, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    title: Mapped[str]
    number_of_pages: Mapped[int] = mapped_column(server_default="0")
    published_date: Mapped[str | None]

    authors: Mapped[list["Author"]] = relationship(
        secondary=book_authors, back_populates="books"
    )

    shelf_id: Mapped[int | None] = mapped_column(ForeignKey("shelves.id"))
    shelf: Mapped["Shelf | None"] = relationship(back_populates="books")

    def __repr__(self):
        return f"Book(id={self.id}, title={self.title!r}, shelf={self.shelf.name!r}, user={self.shelf.user.name!r})"

    def to_dict(self):
        shelf = self.shelf.name if self.shelf else None
        if shelf and self.shelf.user:
            user = self.shelf.user.name

        return {
            "id": self.id,
            "title": self.title,
            "authors": [a.name for a in self.authors],
            "number_of_pages": self.number_of_pages,
            "pushed_date": self.published_date,
            "shelf": shelf,
            "user": user,
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

    books: Mapped[list["Book"]] = relationship(back_populates="shelf")


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    shelves: Mapped[list["Shelf"]] = relationship(back_populates="user")


def get_or_create[T](model: type[T], **filters) -> T:
    obj = db.session.scalar(select(model).filter_by(**filters))
    if obj is None:
        obj = model(**filters)
        db.session.add(obj)
        db.session.flush()
    return obj
