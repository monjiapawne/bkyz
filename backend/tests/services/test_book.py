import pytest

from app.data.models import FetchStatus
from app.services.book import fetch_book
from tests.helpers import assert_dict_subset


@pytest.mark.parametrize(
    ("name", "isbn", "exp_json", "exp_status"),
    [
        (
            "good isbn",
            "978-1718503540",
            {
                "authors": ["OccupyTheWeb"],
                "title": "Linux Basics for Hackers",
                "publish_date": "2024",
            },
            FetchStatus.ok,
        ),
        ("not found isbn", "978-9999999999", {}, FetchStatus.not_found),
    ],
)
def test_fetch_book(name: str, isbn: str, exp_json: dict, exp_status: FetchStatus):
    r = fetch_book(isbn)
    assert r.status == exp_status
    assert_dict_subset(r.dict_, exp_json, name=name)
