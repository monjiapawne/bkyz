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

from app import spec
from app.api.schemas import Out
from app.data.models import Book
from app.errors import BadRequestError
from app.services.book import fetch_book
from app.services.cover import fetch_cover

logger = logging.getLogger(__name__)

books = Blueprint("books", __name__)


class BookIn(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    title: str | None = Field(None, examples=["Just For Fun"])
    authors: str | None = Field(None, examples=["Linus Torvalds, David Diamond"])
    """Comma seperated author names."""
    pages: int = 1
    isbn: str | None = None
    """ISBN 13 only.
    Note this will attempt to fill missing fields based on an isbn lookup."""
    lookup: bool = True
    """If true and isbn is provided thebackend will attempt to lookup the book details from an external source."""

    @model_validator(mode="after")
    def title_or_isbn(self):
        if not (self.title or self.isbn):
            raise ValueError("Provide either a title or isbn")
        return self

    @model_validator(mode="after")
    def check_isbn(self):
        if self.isbn is None:
            return self

        isbn = Book.normalize_isbn(self.isbn)
        if isbn is None or len(isbn) != 13:
            raise ValueError(f"ISBN {self.isbn!r} format is invalid")

        self.isbn = isbn
        return self


class BookOut(Out):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    authors: list[str]
    pages: int
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
    pages: int | None = None
    publish_date: str | None = None


@books.post("")
@spec.validate(json=BookIn, resp=Response(HTTP_200=BookOut, HTTP_201=BookOut))
def create_book(json: BookIn):
    """Add a book to the library.

    If an ISBN is provided, metadata is auto-filled.
    """
    book = json.model_dump(exclude_none=True)

    fetch_status = None
    isbn = Book.normalize_isbn(json.isbn)

    if json.lookup and isbn:
        if existing := Book.get_by_isbn(isbn):
            return BookOut.json_(existing), 200

        # Merge the two looked up, input fields taking priority
        result = fetch_book(isbn)
        fetch_status = result.status

        if result.ok:
            book = result.dict_ | book

    # Extract the fields
    title = book.get("title")
    if not title:
        raise BadRequestError("title is required")

    book = Book.create(
        title=title,
        authors=book.get("authors"),
        pages=book.get("pages"),
        publish_date=book.get("publish_date"),
        isbn=isbn if isbn else None,
        fetch_status=fetch_status,
    )

    if isbn:
        fetch_cover(current_app.config["COVERS_DIR"], book.id, isbn)

    return BookOut.json_(book), 201


@books.patch("/<int:book_id>")
@spec.validate(json=BookPatch)
def update_book(book_id: int, json: BookPatch):
    """Modify a book."""
    book = Book.get_by_id(book_id)

    changes = json.model_dump(exclude_unset=True, exclude_none=True)
    book.update(**changes)

    return BookOut.json_(book)


@books.get("/<int:book_id>")
def get_book(book_id: int):
    """Get a book."""
    book = Book.get_by_id(book_id)
    return BookOut.json_(book), 200


class BookQuery(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    isbn: str | None = None
    """Filter by ISBN 13."""
    title: str | None = None

    @field_validator("isbn")
    @classmethod
    def norm_isbn(cls, v: str | None) -> str | None:
        return Book.normalize_isbn(v)


@books.get("")
@spec.validate(query=BookQuery)
def list_books(query: BookQuery):
    """Gets the list of books."""
    filters = []
    if query.isbn:
        filters.append(Book.isbn == query.isbn)
    if query.title:
        filters.append(Book.title.ilike(f"%{query.title}%"))

    return {"books": [BookOut.json_(b) for b in Book.get_all(*filters)]}


@books.delete("/<int:book_id>")
def delete_book(book_id: int):
    """Delete a book."""
    Book.delete_by_id(book_id)
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
