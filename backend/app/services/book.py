import logging

import requests

from app.services import OPENLIB_HEADERS

TIMEOUT = 5

logger = logging.getLogger(__name__)


def lookup_isbn(isbn: str) -> dict:
    s = requests.session()
    s.headers.update(**OPENLIB_HEADERS)

    r = s.get(f"https://openlibrary.org/isbn/{isbn}", timeout=TIMEOUT)

    book = r.json() if r.ok else {}

    if authors := book.get("authors"):
        ids = [v.get("key").split("/")[-1] for v in authors]

        if auths := _lookup_authors(s, ids):
            book["authors"] = auths

    return book


def _lookup_authors(s: requests.Session, author_ids: list[str] | None) -> list[str] | None:
    authors = []
    for author_id in author_ids:
        print(f"Looking up {author_id}")
        resp = s.get(
            f"https://openlibrary.org/authors/{author_id}.json",
            headers=OPENLIB_HEADERS,
            timeout=TIMEOUT,
        ).json()
        authors.append(resp.get("name"))
    return authors
