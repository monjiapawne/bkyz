from flask import Blueprint, request
from sqlalchemy import select

from app import db
from app.models import Author, Book, Shelf, User, get_or_create
from app.services.isbn import lookup_isbn

bp = Blueprint("books", __name__)


@bp.get("/")
def list_books():
    return [b.to_dict() for b in db.session.scalars(select(Book))]


@bp.post("/<user_name>/<shelf_name>")
def add_book(user_name: str, shelf_name: str):
    user = get_or_create(User, name=user_name)
    # Shouldn't create users only shelfs here
    shelf = get_or_create(Shelf, user_id=user.id, name=shelf_name)

    b = request.get_json()

    if isbn := b.get("isbn"):
        isbn_res = lookup_isbn(isbn)
        b = isbn_res | b

    book = Book(
        title=b.get("title"),
        authors=[
            get_or_create(Author, name=n) for n in b.get("authors", "").split(",")
        ],
        number_of_pages=b.get("number_of_pages"),
        published_date=b.get("published_date"),
        shelf=shelf,
    )

    db.session.add(book)
    db.session.commit()

    return book.to_dict(), 201
