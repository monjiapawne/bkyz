import logging
from dataclasses import dataclass, field

import requests

from app.data.models import FetchStatus
from app.services import OPENLIB_HEADERS

TIMEOUT = 5

logger = logging.getLogger(__name__)


@dataclass
class FetchResult:
    """Helper for external fetches to"""

    status: FetchStatus
    dict_: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == FetchStatus.ok


def fetch_book(isbn: str) -> FetchResult:
    """Fetches book info from external source"""
    with requests.session() as s:
        s.headers.update(OPENLIB_HEADERS)
        return _openlib_fetch_book(s, isbn)


def _openlib_fetch_book(s: requests.Session, isbn: str) -> FetchResult:
    try:
        r = s.get(f"https://openlibrary.org/isbn/{isbn}", timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        return FetchResult(FetchStatus.unreachable)
    except requests.exceptions.Timeout:
        return FetchResult(FetchStatus.timeout)

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        status = (
            FetchStatus.not_found if r.status_code == 404 else FetchStatus.http_error
        )

        return FetchResult(status)

    try:
        book = r.json()
    except requests.exceptions.JSONDecodeError:
        return FetchResult(FetchStatus.invalid_format)

    raw_author_ids = book.get("authors")
    if not raw_author_ids:
        return FetchResult(FetchStatus.ok, book)

    author_ids = [k.split("/")[-1] for v in raw_author_ids if (k := v.get("key"))]

    names = _lookup_authors(s, author_ids)

    if not names:
        return FetchResult(FetchStatus.ok, book)

    book["authors"] = names

    return FetchResult(FetchStatus.ok, book)


def _lookup_authors(s: requests.Session, author_ids: list[str] | None) -> list[str]:
    if author_ids is None:
        return []

    authors = []
    for author_id in author_ids:
        try:
            r = s.get(
                f"https://openlibrary.org/authors/{author_id}.json",
                headers=OPENLIB_HEADERS,
                timeout=TIMEOUT,
            )
            r.raise_for_status()
        # Current logic just skips possible errors. There shouldn't be http errors for
        # these requests, as they're provided by the up stream.
        except requests.exceptions.ConnectionError:
            continue
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.HTTPError:
            continue
        else:
            if name := r.json().get("name"):
                authors.append(name)

    return authors


def search_book(**kwargs):
    """Fetches book info from external source"""
    with requests.session() as s:
        s.headers.update(OPENLIB_HEADERS)
        return _openlib_search_book(s, **kwargs)


def _openlib_search_book(s: requests.Session, title: str, size: str = "M"):
    URL = "https://openlibrary.org/search.json"

    params = {
        "title": title,
        "fields": ["author_name", "title", "publish_date", "isbn"],
        "limit": 1,
        "sort": "new",
    }
    response = s.get(URL, params=params)

    book_info = response.json().get("docs")[0]

    isbn = book_info["isbn"][0]

    cover = f"https://covers.openlibrary.org/b/isbn/{isbn}-{size}.jpg"

    book_final = {
        "author": book_info["author_name"],
        "title": book_info["title"],
        "published": book_info["publish_date"][0],
        "isbn": isbn,
        "cover": cover,
    }

    return book_final
