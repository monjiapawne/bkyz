URL = "/api/v1/playlists/1/tracks"

def test_create_track(client_user_playlist):
    client = client_user_playlist
    r = client.post(URL, json={
            "book_id": 0,
            "current_page": 1,
            "medium": "physical"
        }
    )
    assert r.status_code == 201
