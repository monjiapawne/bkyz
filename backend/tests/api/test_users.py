def test_create_user(client_user):
    client = client_user
    r = client.get("/user")
    assert r.status_code == 200
