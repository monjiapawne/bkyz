import requests


def lookup_isbn(isbn: str) -> dict:
    url = f"https://openlibrary.org/isbn/{isbn}"
    r = requests.get(url, headers={"accept": "application/json"})
    return r.json() if r.ok else {}
