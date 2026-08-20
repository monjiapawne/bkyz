import logging

import requests
from flask import current_app

from app.errors import APIError

logger = logging.getLogger(__name__)

HEADERS = {
    "accept": "application/json",
    "User-Agent": "bkyz/0.1.0 <187591672+monjiapawne@users.noreply.github.com>",
}
TIMEOUT = 2


def fetch_cover(book_id: int, isbn: str) -> None:
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg?default=false"
    r = requests.get(url, headers=HEADERS | {"accept": "image/*"}, timeout=TIMEOUT)
    with open(current_app.config["COVERS_DIR"] / f"{book_id}.jpg", "wb") as f:
        f.write(r.content)


def lookup_isbn(isbn: str) -> dict:
    url = f"https://openlibrary.org/isbn/{isbn}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        res = r.json() if r.ok else {}

        if authors_dict := res.get("authors"):
            res["authors"] = []
            for author in authors_dict:
                author_id = author["key"].split("/")[-1]
                a = requests.get(
                    f"https://openlibrary.org/authors/{author_id}.json",
                    headers=HEADERS,
                    timeout=TIMEOUT,
                ).json()
                res["authors"].append(a.get("name"))
    except requests.RequestException as e:
        logger.warning(f"isbn lookup failed isbn={isbn}")
        raise APIError("ISBN lookup is unavailable", 503) from e

    return res
