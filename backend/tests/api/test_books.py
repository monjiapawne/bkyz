import pytest

URL = "/api/v1/books"


def test_post_book_with_title(client):
    r = client.post(URL, json={"title": "Dune"})
    assert r.status_code == 201
    assert r.get_json()["title"] == "Dune"

    books = client.get(URL).get_json()["books"]
    assert [b["title"] for b in books] == ["Dune"]


def test_post_book_with_no_title(client):
    r = client.post(URL, json={"authors": "hello, world"})
    assert r.status_code == 422


def test_create_book_with_isbn_13(client):
    r = client.post(URL, json={"isbn": "978-1718503540"})
    if r.status_code == 503:
        pytest.skip("ISBN lookup timed out")

    j = r.get_json()

    assert j["title"] == "Linux Basics for Hackers"
    assert len(j["authors"]) == 1
    assert j["authors"] == ["OccupyTheWeb"]
    assert j["publish_date"] == "2024"


def test_post_book_with_author(client):
    r = client.post(URL, json={"title": "Dune", "authors": "hello, world"})
    assert r.get_json()["authors"] == ["hello", "world"]


def test_patch_book(client):
    r = client.post(URL, json={"title": "Dune"})
    book_id = str(r.get_json()["id"])
    r = client.patch(f"{URL}/{book_id}", json={"title": "NotDune"})
    assert r.get_json()["title"] == "NotDune"


def test_patch_book_invalid_fields(client):
    r = client.post(URL, json={"title": "Dune"})
    book_id = str(r.get_json()["id"])
    r = client.patch(
        f"{URL}/{book_id}", json={"title": "NotDune", "fake_field": "value"}
    )
    assert r.status_code == 422
