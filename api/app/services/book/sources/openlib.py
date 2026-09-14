from app.services.result import NotFoundError, fetch_result

from ._base import BookClient


class Openlib(
    BookClient,
    headers={
        "accept": "application/json",
        "User-Agent": "bkyz/0.1.0 example@example.com>",
    },
):
    @fetch_result
    def by_isbn(self, isbn: str) -> dict:
        url = "https://openlibrary.org/search.json"
        params = {
            "isbn": isbn,
            "fields": "title,author_name,publish_date,number_of_pages_median,cover_i",
            "sort": "new",
        }
        r = self.s.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()

        res_json = r.json()

        if res_json["numFound"] == 0:
            raise NotFoundError

        b = res_json["docs"][0]
        book = {}
        book["title"] = b.get("title")
        book["publish_date"] = b.get("publish_date", [])[-1]
        book["authors"] = b.get("author_name", "")
        book["pages"] = b.get("number_of_pages_median")
        return book

    @fetch_result
    def by_title(self, title: str, size: str = "M") -> dict:
        URL = "https://openlibrary.org/search.json"

        params = {
            "title": title,
            "fields": ["author_name", "title", "publish_date", "isbn"],
            "limit": 1,
            "sort": "new",
        }

        response = self.s.get(URL, params=params, timeout=self.timeout)

        book_info = response.json().get("docs")[0]

        isbn = book_info["isbn"][0]

        book_final = {
            "author": book_info["author_name"],
            "title": book_info["title"],
            "published": book_info["publish_date"][0],
            "isbn": isbn,
        }

        return book_final
