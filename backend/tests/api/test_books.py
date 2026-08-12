def test_create_book_with_title(client):
    r = client.post("/api/v1/books/", json={"title": "Dune"})
    assert r.status_code == 201
    assert r.get_json()["title"] == "Dune"

    books = client.get("/api/v1/books/").get_json()
    assert [b["title"] for b in books] == ["Dune"]


# Disabled for now, need to fix and add a timeout to requests
# Currently this freezes if there's issues on the OpenLib api.
# Probably should monkey patch anyways.
#
# def test_create_book_with_isbn(client):
#     r = client.post("/api/v1/books/", json={"isbn": "1718503547"})
#     assert r.get_json()["title"] == "Linux Basics for Hackers"
