import pytest

from app.data.models import FetchStatus
from app.services.book import fetch_book
from tests.helpers import assert_dict_subset


@pytest.mark.parametrize(
    ("name", "isbn", "exp_json", "exp_status"),
    [
        (
            "good isbn",
            "9781718503540",
            {
                "authors": ["OccupyTheWeb"],
                "title": "Linux Basics for Hackers",
                "publish_date": "2024",
            },
            FetchStatus.ok,
        ),
        ("not found isbn", "9789999999999", {}, FetchStatus.not_found),
    ],
)
def test_fetch_book(name: str, isbn: str, exp_json: dict, exp_status: FetchStatus):
    r = fetch_book(isbn=isbn)
    print(r.dict_)
    assert r.status == exp_status, f"status not matched, expected: {exp_status}, got {r.status}"
    assert_dict_subset(r.dict_, exp_json, name=name)


def test_search_book():
    res = fetch_book(title="head first python").dict_

    assert res["author"] == ["Paul Barry"]
    assert res["isbn"] == "9789350231883"
    assert res["title"] == "Head First Python"
