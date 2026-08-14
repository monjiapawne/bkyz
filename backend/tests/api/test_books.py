URL = "/api/v1/books/"


def test_post_book_with_title(client):
    r = client.post(URL, json={"title": "Dune"})
    assert r.status_code == 201
    assert r.get_json()["title"] == "Dune"

    books = client.get(URL).get_json()
    assert [b["title"] for b in books] == ["Dune"]


def test_post_book_with_no_title(client):
    r = client.post(URL, json={"authors": "hello, world"})
    assert r.status_code == 400


# def test_create_book_with_isbn(client):
#     r = client.post(URL, json={"isbn": "1718503547"})
#     assert r.get_json()["title"] == "Linux Basics for Hackers"


def test_post_book_with_author(client):
    r = client.post(URL, json={"title": "Dune", "authors": "hello, world"})
    assert r.get_json()["authors"] == ["hello", "world"]


def test_patch_book(client):
    r = client.post(URL, json={"title": "Dune"})
    book_id = str(r.get_json()["id"])
    r = client.patch(URL + book_id, json={"title": "NotDune"})
    assert r.get_json()["title"] == "NotDune"


def test_patch_book_invalid_fields(client):
    r = client.post(URL, json={"title": "Dune"})
    book_id = str(r.get_json()["id"])
    r = client.patch(URL + book_id, json={"title": "NotDune", "fake_field": "value"})
    assert r.status_code == 422
