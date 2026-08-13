import logging

import requests
from flask import Blueprint, request
from pydantic import BaseModel, ConfigDict, model_validator, Field
from sqlalchemy import select
from spectree import Response

from app import db, spec
from app.errors import APIError, NotFound
from app.models import Author, Book, ShelfBook, get_or_create

logger = logging.getLogger(__name__)

books = Blueprint("books", __name__)


@books.get("/")
def list_books():
    """List all books."""
    return [b.to_dict() for b in db.session.scalars(select(Book))]


class BookIn(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    title: str | None = Field(None, examples=["Just For Fun"])
    authors: str | None = Field(None, examples=["Linus Torvalds, David Diamond"])
    """Comma seperated author names."""
    number_of_pages: int = 1
    isbn: str | None = None

    @model_validator(mode="after")
    def title_or_isbn(self):
        if not (self.title or self.isbn):
            raise APIError("Provide either a title or isbn")
        return self

    @model_validator(mode="after")
    def check_isbn(self):
        if self.isbn is None:
            return self

        self.isbn = Book.normalize_isbn(self.isbn)

        if len(self.isbn) not in (10, 13):
            raise APIError(f"ISBN {self.isbn!r} format is invalid")

        return self

class BookOut(BaseModel):
    id: int
    title: str
    authors: list[str]
    number_of_pages: int
    publish_date: str | None = None
    isbn: str | None = None

@books.post("/")
@spec.validate(json=BookIn, resp=Response(HTTP_200=BookOut, HTTP_201=BookOut))
def create_book(json: BookIn):
    """Add a book to the library.

    If an ISBN is provided, metadata is auto-filled.
    """
    book = json.model_dump(exclude_none=True)
    if isbn := Book.normalize_isbn(json.isbn):
        if existing := Book.lookup_by_isbn(isbn):
            return existing.to_dict(), 200

        # Merge the two looked up, input fields taking priority
        book = lookup_isbn(isbn) | book

    # Extract the fields
    title = book.get("title")
    if not title:
        raise APIError("title is required")

    authors = book.get("authors") or []
    if isinstance(authors, str):
        authors = [n for n in book.get("authors", "").split(",") if n.strip()]

    book = Book(
        title=title,
        authors=[get_or_create(Author, name=a.strip()) for a in authors],
        number_of_pages=book.get("number_of_pages"),
        publish_date=book.get("publish_date"),
        isbn=isbn,
    )
    db.session.add(book)
    db.session.commit()

    logger.info(f"book created id={book.id} title={book.title!r}")

    return book.to_dict(), 201


@books.patch("/<int:book_id>")
def update_book(book_id: int):
    """Modify a book's metadata.

    TODO: fix implementation
    """
    PATCHABLE = {"title", "number_of_pages", "publish_data", "authors"}

    if not (book := db.session.get(Book, book_id)):
        raise NotFound(f"book {book_id} does not exist")

    changes = request.get_json()
    for f, v in changes.items():
        if f not in PATCHABLE:
            raise APIError(f"unknown or read-only field: {f}")
        if f == "authors":
            v = [get_or_create(Author, name=n.strip()) for n in v.split(",") if n.strip()]
        setattr(book, f, v)

    db.session.commit()
    return book.to_dict()


@books.delete("/<int:book_id>")
def delete_book(book_id: int):
    """Delete a book.

    Only permitted if, book is not currently in use in a shelf.
    """
    book = db.session.get(Book, book_id)
    if not book:
        raise NotFound(f"book {book_id} does not exist")

    in_use = db.session.scalar(select(ShelfBook).where(ShelfBook.book_id == book_id))
    if in_use:
        raise APIError("book is on shelves and cannot be delete", status=409)

    db.session.delete(book)
    db.session.commit()

    logger.info(f"deleted book id={book.id} title={book.title!r}")
    return "", 204


def lookup_isbn(isbn: str) -> dict:
    url = f"https://openlibrary.org/isbn/{isbn}"
    headers = {"accept": "application/json"}
    r = requests.get(url, headers=headers)
    res = r.json() if r.ok else {}
    if authors_dict := res.get("authors"):
        res["authors"] = []
        for author in authors_dict:
            author_id = author["key"].split("/")[-1]
            a = requests.get(f"https://openlibrary.org/authors/{author_id}.json", headers=headers).json()
            res["authors"].append(a.get("name"))

    return res
