import logging

import requests

from app.services import OPENLIB_HEADERS

TIMEOUT = 5

logger = logging.getLogger(__name__)


def fetch_book(isbn: str) -> dict:
    """Fetches book info from external source"""
    s = requests.session()
    return _openlib_fetch_book(s, isbn)


def _openlib_fetch_book(s: requests.Session, isbn: str) -> dict | None:
    s.headers.update(OPENLIB_HEADERS)

    r = s.get(f"https://openlibrary.org/isbn/{isbn}", timeout=TIMEOUT)

    if not r.ok:
        return

    try:
        book = r.json()
    except requests.exceptions.JSONDecodeError:
        return

    raw_author_ids = book.get("authors")
    if not raw_author_ids:
        return book

    author_ids = [k.split("/")[-1] for v in raw_author_ids if (k := v.get("key"))]

    names = _lookup_authors(s, author_ids)

    if not names:
        return book

    book["authors"] = names

    return book


def _lookup_authors(
    s: requests.Session, author_ids: list[str] | None
) -> list[str] | None:
    authors = []
    for author_id in author_ids:
        print(f"Looking up {author_id}")
        r = s.get(
            f"https://openlibrary.org/authors/{author_id}.json",
            headers=OPENLIB_HEADERS,
            timeout=TIMEOUT,
        )
        if r.ok and (name := r.json().get("name")):
            authors.append(name)

    return authors
