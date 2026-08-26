def test_list_playlists(client_playist):
    client = client_playist
    r = client.get("/api/v1/playlists")
    assert r.status_code == 200
