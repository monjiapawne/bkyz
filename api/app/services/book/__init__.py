from app.services.result import FetchResult

from .sources.openlib import Openlib

_openlib = Openlib(timeout=10.0)


def fetch_book(*, isbn: str | None = None, title: str | None = None) -> FetchResult:
    if isbn:
        return _openlib.by_isbn(isbn)
    if title:
        return _openlib.by_title(title)
