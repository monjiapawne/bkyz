import pytest

URL = "/books"


@pytest.mark.parametrize(
    ("name", "req_json", "exp_json", "exp_status"),
    [
        ("title only", {"title": "Dune"}, {"title": "Dune"}, 201),
        ("ignore fields", {"title": "Dune", "taco": "salad"}, {"title": "Dune"}, 201),
        (
            "author and title",
            {"title": "Dune", "authors": "author 1, author2"},
            {"authors": ["author 1", "author2"]},
            201,
        ),
        (
            "all fields",
            {
                "title": "Python",
                "authors": "Al Sweigart",
                "pages": 504,
            },
            {
                "title": "Python",
                "authors": ["Al Sweigart"],
                "pages": 504,
            },
            201,
        ),
        ("no values", {}, {}, 422),
    ],
)
def test_create_book(client, name: str, req_json: dict, exp_json: dict, exp_status: int):
    r = client.post("/books", json=req_json)
    assert r.status_code == exp_status
    resp_json = r.get_json()
    print(r.text)
    for exp_k, exp_v in exp_json.items():
        try:
            resp_v = resp_json[exp_k]
        except KeyError:
            pytest.fail(f"[{name}] missing key {exp_k!r} in {resp_json}\nresponse: {r.text}")

        assert resp_v == exp_v


def test_create_book_with_isbn_13(client):
    # this probably shouldn't be here, or at least should be mocked the external response..
    r = client.post("/books", json={"isbn": "978-1718503540"})
    if r.status_code == 503:
        pytest.skip("ISBN lookup timed out")

    j = r.get_json()

    assert j["title"] == "Linux Basics for Hackers"
    assert len(j["authors"]) == 1
    assert j["publish_date"] == "2024"


def test_patch_book(client):
    r = client.post("/books", json={"title": "Dune"})
    book_id = str(r.get_json()["id"])
    r = client.patch(f"/books/{book_id}", json={"title": "NotDune"})
    assert r.get_json()["title"] == "NotDune"


def test_patch_book_invalid_fields(client):
    r = client.post("/books", json={"title": "Dune"})
    book_id = str(r.get_json()["id"])
    r = client.patch(f"/books/{book_id}", json={"title": "NotDune", "fake_field": "value"})
    assert r.status_code == 422
