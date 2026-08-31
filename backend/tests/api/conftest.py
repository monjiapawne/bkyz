import pytest
from flask.testing import FlaskClient

from app import create_app, db


class APIClient(FlaskClient):
    def open(self, path, *args, **kwargs):
        prefix = "/api/v1"
        return super().open(f"{prefix}{path}", *args, **kwargs)


@pytest.fixture
def client():
    app = create_app("config.TestingConfig")
    app.test_client_class = APIClient
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client_book(client):
    client.post("/books", json={"title": "Dune"})
    return client


@pytest.fixture
def client_user(client_book):
    client = client_book
    client.post(
        "/user/register",
        json={"username": "testuser", "password": "testpassword"},
    )
    client.post("/user/login", json={"username": "testuser", "password": "testpassword"})
    return client


@pytest.fixture
def client_playlist(client_user):
    client = client_user
    r = client.post("/playlists", json={"name": "unamed", "description": "Empty."})
    assert r.status_code == 201
    r = client.get("/playlists")
    assert r.status_code == 200
    assert r.get_json()[0]["description"] == "Empty."
    assert r.get_json()[0]["name"] == "unamed"

    return client


@pytest.fixture
def client_track(client_playlist):
    client = client_playlist
    r = client.post(
        "/playlists/1/tracks",
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
