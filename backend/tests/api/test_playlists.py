def test_list_playlists(client_user_playlist):
    client = client_user_playlist
    r = client.get("/api/v1/playlists")
    assert r.status_code == 200
