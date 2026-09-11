import pytest

from tests.helpers import assert_status_code


@pytest.mark.parametrize(
    ("name", "req_json", "exp_json", "exp_status"),
    [
        (
            "single track",
            {
                "book_id": 1,
                "position": 1,
                "medium": "physical",
                "unit": "pages",
                "total": 100,
            },
            {
                "book_id": 1,
                "id": 1,
                "medium": "physical",
                "position": 1,
                "total": 100,
                "unit": "pages",
            },
            201,
        ),
        (
            "invalid book_id",
            {
                "book_id": 99,
            },
            {},
            404,
        ),
    ],
)
def test_create_track(client_playlist, name: str, req_json: dict, exp_json: dict, exp_status: int):
    client = client_playlist

    r = client.post("/playlists/1/tracks", json=req_json)
    assert_status_code(exp_status, r)

    if not exp_json:
        return

    track_id = r.get_json()["id"]
    r = client.get(f"/playlists/1/tracks/{track_id}")
    assert_status_code(200, r)


def test_delete_track(client_track):
    client = client_track
    r = client.delete("/playlists/1/tracks/1")
    assert_status_code(204, r)

    r = client.get("/playlists/1/tracks")
    assert_status_code(200, r)
    assert len(r.get_json()["tracks"]) == 0


def test_progress_track(client_track):
    client = client_track
    r = client.post("/playlists/1/tracks/1/progress", json={"position": 49})
    assert r.get_json()["position"] == 50


def test_update_track(client_track):
    client = client_track
    r = client.patch("/playlists/1/tracks/1", json={"medium": "pdf"})
    assert r.get_json()["medium"] == "pdf"
