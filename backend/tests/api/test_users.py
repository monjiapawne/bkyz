def test_create_user(client_with_user):
    client = client_with_user
    r = client.get("api/v1/user")
    assert r.status_code == 200
