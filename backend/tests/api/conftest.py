import pytest

from app import create_app, db


@pytest.fixture
def client():
    app = create_app("config.TestingConfig")
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client_book(client):
    client.post("/api/v1/books", json={"title": "Dune"})
    return client


@pytest.fixture
def client_user(client_book):
    client = client_book
    client.post(
        "/api/v1/user/register",
        json={"username": "testuser", "password": "testpassword"},
    )
    client.post("/api/v1/user/login", json={"username": "testuser", "password": "testpassword"})
    return client


@pytest.fixture
def client_playist(client_user):
    client = client_user
    r = client.post("/api/v1/playlists", json={"name": "unamed", "description": "Empty."})
    assert r.status_code == 201
    r = client.get("/api/v1/playlists")
    assert r.status_code == 200
    assert r.get_json()[0]["description"] == "Empty."
    assert r.get_json()[0]["name"] == "unamed"

    return client


@pytest.fixture
def client_track(client_playist):
    client = client_playist
    r = client.post(
        "/api/v1/playlists/1/tracks",
        json={
            "book_id": 1,
            "position": 1,
            "medium": "physical",
            "unit": "pages",
            "total": 100,
        },
    )

    assert r.status_code == 201
    j = r.get_json()
    assert j["medium"] == "physical"
    assert j["position"] == 1
    assert j["unit"] == "pages"
    assert j["total"] == 100

    return client
