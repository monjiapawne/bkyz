def test_list_playlists(client_playlist):
    client = client_playlist
    r = client.get("/playlists")
    assert r.status_code == 200
