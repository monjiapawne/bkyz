def test_list_playlists(client_playist):
    client = client_playist
    r = client.get("/playlists")
    assert r.status_code == 200
