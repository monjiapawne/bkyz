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
def client_with_user(client):
    client.post(
        "/api/v1/user/register",
        json={"username": "testuser", "password": "testpassword"},
    )
    client.post(
        "/api/v1/user/login", json={"username": "testuser", "password": "testpassword"}
    )
    return client


@pytest.fixture
def client_user_playlist(client_with_user):
    client = client_with_user
    r = client.post(
        "/api/v1/playlists", json={"name": "unamed", "description": "Empty."}
    )
    assert r.status_code == 201
    r = client.get("/api/v1/playlists")
    assert r.status_code == 200
    assert r.get_json()[0]["description"] == "Empty."
    assert r.get_json()[0]["name"] == "unamed"

    return client
