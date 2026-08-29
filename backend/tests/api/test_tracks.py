URL = "/playlists/1/tracks"


def test_create_track(client_track):
    client = client_track
    r = client.get("/playlists/1/tracks")

    assert r.status_code == 200
    assert len(r.get_json()["tracks"]) == 1


def test_delete_track(client_track):
    client = client_track
    r = client.delete("/playlists/1/tracks/1")
    assert r.status_code == 204

    r = client.get("/playlists/1/tracks")
    assert r.status_code == 200
    assert len(r.get_json()["tracks"]) == 0


def test_progress_track(client_track):
    client = client_track
    r = client.post("/playlists/1/tracks/1/progress", json={"position": 49})
    assert r.get_json()["position"] == 50


def test_update_track(client_track):
    client = client_track
    r = client.patch("/playlists/1/tracks/1", json={"medium": "pdf"})
    assert r.get_json()["medium"] == "pdf"
