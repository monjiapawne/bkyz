import pytest


@pytest.fixture
def client_registered(client):
    r = client.post("/user/register", json={"username": "testuser1", "password": "valid_password1"})
    assert r.status_code == 201
    return client


@pytest.mark.parametrize(
    ("name", "req_json", "exp_status"),
    [
        ("duplicate username", {"username": "testuser1", "password": "different_pw1"}, 409),
        ("free username", {"username": "testuser2", "password": "valid_password1"}, 201),
    ],
)
def test_register(client_registered, name: str, req_json: dict, exp_status: int):
    client = client_registered
    r = client.post("/user/register", json=req_json)
    assert r.status_code == exp_status, (
        f"{name}: expected {exp_status}, got {r.status_code}\n response: {r.text}"
    )
