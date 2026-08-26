import requests

from app.services import OPENLIB_HEADERS

TIMEOUT = 2


def fetch_cover(covers_dir: str, book_id: int, isbn: str) -> None:
    # TODO: We should store the different sizes required by the frontend
    # TODO: We should store the response in the database and then check before re-requesting
    # from openlib. If it's missing from openlib it should just be skipped on future posts of the isbn.
    # Not fully convinced it's needed yet.
    size = "M"
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-{size}.jpg?default=false"

    try:
        r = requests.get(
            url, headers=OPENLIB_HEADERS | {"accept": "image/*"}, timeout=TIMEOUT
        )
    except requests.exceptions.RequestException:
        # For now just skip, don't propegate
        pass
    else:
        with open(covers_dir / f"{book_id}.jpg", "wb") as f:
            f.write(r.content)
