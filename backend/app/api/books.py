import logging

from flask import Blueprint, current_app, send_file, url_for
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)
from spectree import Response

from app import db, spec
from app.data.models import Book
from app.errors import APIError, NotFound
from app.services.book import fetch_book
from app.services.cover import fetch_cover

logger = logging.getLogger(__name__)

books = Blueprint("books", __name__)


class BookIn(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    title: str | None = Field(None, examples=["Just For Fun"])
    authors: str | None = Field(None, examples=["Linus Torvalds, David Diamond"])
    """Comma seperated author names."""
    number_of_pages: int | None = None
    isbn: str | None = None
    """ISBN 13 only.
    Note this will attempt to fill missing fields based on an isbn lookup."""

    @model_validator(mode="after")
    def title_or_isbn(self):
        if not (self.title or self.isbn):
            raise ValueError("Provide either a title or isbn")
        return self

    @model_validator(mode="after")
    def check_isbn(self):
        if self.isbn is None:
            return self

        self.isbn = Book.normalize_isbn(self.isbn)

        if len(self.isbn) != 13:
            raise ValueError(f"ISBN {self.isbn!r} format is invalid")

        return self


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    authors: list[str]
    number_of_pages: int
    publish_date: str | None = None
    isbn: str | None = None

    @field_validator("authors", mode="before")
    @classmethod
    def flatten_authors(cls, v: list) -> list[str]:
        return [a if isinstance(a, str) else a.name for a in v]

    @computed_field
    @property
    def cover_url(self) -> str:
        return url_for("api.books.get_book_cover", book_id=self.id, _external=True)


class BookPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    authors: str | None = None
    number_of_pages: int | None = None
    publish_date: str | None = None


@books.get("")
def list_books():
    """List all books."""
    return {"books": [BookOut.model_validate(b).model_dump() for b in Book.get_all()]}


@books.post("")
@spec.validate(json=BookIn, resp=Response(HTTP_200=BookOut, HTTP_201=BookOut))
def create_book(json: BookIn):
    """Add a book to the library.

    If an ISBN is provided, metadata is auto-filled.
    """
    book: BookIn = json.model_dump(exclude_none=True)

    if isbn := Book.normalize_isbn(json.isbn):
        if existing := Book.get_by_isbn(isbn):
            return BookOut.model_validate(existing).model_dump(), 200

        # Merge the two looked up, input fields taking priority
        if external_book_data := fetch_book(isbn):
            book = external_book_data | book

    # Extract the fields
    title = book.get("title")
    if not title:
        raise APIError("title is required")

    book = Book.create(
        title=title,
        authors=book.get("authors"),
        number_of_pages=book.get("number_of_pages"),
        publish_date=book.get("publish_date"),
        isbn=isbn,
    )

    if isbn:
        fetch_cover(current_app.config["COVERS_DIR"], book.id, isbn)

    return BookOut.model_validate(book).model_dump(), 201


@books.patch("/<int:book_id>")
@spec.validate(json=BookPatch)
def update_book(book_id: int, json: BookPatch):
    """Modify a book."""
    if not (book := Book.get_by_id(book_id)):
        raise NotFound(f"book {book_id} does not exist")

    for f, v in json.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(book, f, v)

    db.session.commit()
    return BookOut.model_validate(book).model_dump()


@books.get("/<int:book_id>")
def get_book(book_id: int):
    """Get a book."""
    if not (book := Book.get_by_id(book_id)):
        raise NotFound(f"book {book_id} does no exist")

    return BookOut.model_validate(book).model_dump()


@books.delete("/<int:book_id>")
def delete_book(book_id: int):
    """Delete a book."""
    if not Book.delete_by_id(book_id):
        raise NotFound(f"No Book found with id: {book_id}")

    (current_app.config["COVERS_DIR"] / f"{book_id}.jpg").unlink(missing_ok=True)
    return "", 204


@books.get("/<int:book_id>/cover")
def get_book_cover(book_id: int):
    """Get a book cover."""
    covers_dir = current_app.config["COVERS_DIR"]
    cover = covers_dir / f"{book_id}.jpg"

    if not cover.is_file():
        return send_file(current_app.config["PLACEHOLDER_COVER"], max_age=300)

    return send_file(cover, max_age=86400)
