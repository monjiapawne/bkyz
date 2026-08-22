from typing import Literal

import requests
from flask import current_app

from app.services import OPENLIB_HEADERS

TIMEOUT = 2


def fetch_cover(book_id: int, isbn: str, size: Literal["S", "M", "L"] = "M") -> None:
    # TODO: We should store the different sizes required by the frontend
    # TODO: We should store the response in the database and then check before re-requesting
    # from openlib. If it's missing from openlib it should just be skipped on future posts of the isbn.
    # Not fully convinced it's needed yet.
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-{size}.jpg?default=false"

    r = requests.get(
        url, headers=OPENLIB_HEADERS | {"accept": "image/*"}, timeout=TIMEOUT
    )

    with open(current_app.config["COVERS_DIR"] / f"{book_id}.jpg", "wb") as f:
        f.write(r.content)
