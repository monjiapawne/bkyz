import logging

import requests
from flask import Blueprint, request
from sqlalchemy import select

from app import db
from app.errors import APIError, NotFound
from app.models import Author, Book, ShelfBook, get_or_create

logger = logging.getLogger(__name__)

bp = Blueprint("books", __name__)


@bp.get("/")
def list_books():
    """List all books."""
    return [b.to_dict() for b in db.session.scalars(select(Book))]


@bp.post("/")
def create_book():
    """Add a book to the library.

    If an ISBN is provided, metadata is auto-filled and existing
    books are returned instead of duplicated (200 vs 201).
    """
    b = request.get_json()

    if isbn := Book.normalize_isbn(b.get("isbn")):
        if existing := db.session.scalar(select(Book).where(Book.isbn == isbn)):
            return existing.to_dict(), 200
        b = lookup_isbn(isbn) | b

    title = b.get("title")
    if not title:
        raise APIError("title is required")

    book = Book(
        title=title,
        authors=[get_or_create(Author, name=n.strip()) for n in b.get("authors", "").split(",") if n.strip()],
        number_of_pages=b.get("number_of_pages"),
        publish_date=b.get("publish_date"),
        isbn=isbn,
    )

    db.session.add(book)
    db.session.commit()

    logger.info(f"book created id={book.id} title={book.title!r}")

    return book.to_dict(), 201


@bp.patch("/<int:book_id>")
def update_book(book_id: int):
    """Modify a book's metadata."""
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


@bp.delete("/<int:book_id>")
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
    r = requests.get(url, headers={"accept": "application/json"})
    return r.json() if r.ok else {}
