def test_list_playlists(client_playlist):
    client = client_playlist
    r = client.get("/playlists")
    assert r.status_code == 200

def test_patch_playlist(client_playlist):
    client = client_playlist
    client.patch("/playlists/1", json={"name": "patch_test"})
    r = client.get("/playlists/1")
    assert r.get_json()['name'] == "patch_test"
    