import pytest

def test_create_book_with_title(client):
    r = client.post("/api/v1/books/", json={"title": "Dune"})
    assert r.status_code == 201
    assert r.get_json()["title"] == "Dune"

    books = client.get("/api/v1/books/").get_json()
    assert [b["title"] for b in books] == ["Dune"]


def test_create_book_with_no_title(client):
    r = client.post("/api/v1/books/", json={"authors": "hello, world"})
    assert r.status_code == 400


def test_create_book_with_isbn(client):
    r = client.post("/api/v1/books/", json={"isbn": "1718503547"})
    assert r.get_json()["title"] == "Linux Basics for Hackers"


def test_create_book_with_author(client):
    r = client.post("/api/v1/books/", json={"title": "Dune", "authors": "hello, world"})
    assert r.get_json()["authors"] == ['hello', 'world']