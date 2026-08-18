from flask import Blueprint
from flask_login import current_user, login_required
from pydantic import BaseModel

from app import spec
from app.errors import NotFound
from app.models import Medium, Playlist, Track

tracks = Blueprint("tracks", __name__)


@tracks.get("")
@login_required
def list_tracks(playlist_id: int):
    """List all tracks of a playlist."""
    playlist = Playlist.get_one(
        Playlist.id == playlist_id, Playlist.user_id == current_user.id
    )
    if playlist is None:
        raise NotFound(f"No Playlist found with id: {playlist_id}")

    return {"tracks": [t.to_json() for t in playlist.tracks]}


@tracks.get("/<int:track_id>")
@login_required
def get_track(playlist_id: int, track_id: int):
    """Get a track."""
    track = Track.get_one(
        Playlist.id == playlist_id,
        Track.id == track_id,
    )
    if not track:
        raise NotFound(
            f"Track id: {track_id} was not found in Playlist id: {playlist_id}"
        )

    return track.to_json(), 200


class TrackIn(BaseModel):
    book_id: int
    current_page: int = 1
    medium: Medium = Medium.physical


@tracks.post("")
@login_required
@spec.validate(json=TrackIn)
def create_track(playlist_id: int, json: TrackIn):
    """Creates a track and adds it to the parent playlist."""
    # Ensure playlist exists
    playlist = Playlist.get_one(
        Playlist.id == playlist_id, Playlist.user_id == current_user.id
    )
    track = Track.create(
        playlist_id=playlist.id,
        book_id=json.book_id,
        current_page=json.current_page,
        medium=json.medium
    )  # fmt: skip
    return track.to_json(), 201


@tracks.delete("/<int:track_id>")
@login_required
def delete_track(playlist_id: int, track_id: int):
    if not Track.delete_by_id(track_id):
        raise NotFound

    return "", 204
