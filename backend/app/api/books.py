import logging

import requests
from flask import Blueprint
from pydantic import BaseModel, ConfigDict, Field, model_validator
from spectree import Response

from app import db, spec
from app.errors import APIError, NotFound
from app.models import Book

logger = logging.getLogger(__name__)

books = Blueprint("books", __name__)


@books.get("")
def list_books():
    """List all books."""
    return {"books": [b.to_json() for b in Book.get_all()]}


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

        if len(self.isbn) not in 13:
            raise ValueError(f"ISBN {self.isbn!r} format is invalid")

        return self


class BookOut(BaseModel):
    id: int
    title: str
    authors: list[str]
    number_of_pages: int
    publish_date: str | None = None
    isbn: str | None = None


@books.post("")
@spec.validate(json=BookIn, resp=Response(HTTP_200=BookOut, HTTP_201=BookOut))
def create_book(json: BookIn):
    """Add a book to the library.

    If an ISBN is provided, metadata is auto-filled.
    """
    book: BookIn = json.model_dump(exclude_none=True)

    if isbn := Book.normalize_isbn(json.isbn):
        if existing := Book.get_by_isbn(isbn):
            return existing.to_json(), 200

        # Merge the two looked up, input fields taking priority
        book = lookup_isbn(isbn) | book

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

    logger.info(f"book created id={book.id} title={book.title!r}")

    return book.to_json(), 201


class BookPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    authors: str | None = None
    number_of_pages: int | None = None
    publish_date: str | None = None


@books.patch("/<int:book_id>")
@spec.validate(json=BookPatch)
def update_book(book_id: int, json: BookPatch):
    """Modify a book."""
    if not (book := Book.get_by_id(book_id)):
        raise NotFound(f"book {book_id} does not exist")

    for f, v in json.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(book, f, v)

    db.session.commit()
    return book.to_json()


@books.delete("/<int:book_id>")
def delete_book(book_id: int):
    """Delete a book."""
    if not Book.delete_by_id(book_id):
        raise NotFound(f"No Book found with id: {book_id}")
    return "", 204


def lookup_isbn(isbn: str) -> dict:
    url = f"https://openlibrary.org/isbn/{isbn}"
    headers = {"accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, timeout=1)
        res = r.json() if r.ok else {}
        if authors_dict := res.get("authors"):
            res["authors"] = []
            for author in authors_dict:
                author_id = author["key"].split("/")[-1]
                a = requests.get(
                    f"https://openlibrary.org/authors/{author_id}.json",
                    headers=headers,
                    timeout=1,
                ).json()
                res["authors"].append(a.get("name"))
    except requests.RequestException as e:
        logger.warning(f"isbn lookup failed isbn={isbn}")
        raise APIError("ISBN lookup is unavailable", 503) from e

    return res
