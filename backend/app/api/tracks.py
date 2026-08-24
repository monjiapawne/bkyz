from flask import Blueprint
from flask_login import current_user, login_required
from pydantic import BaseModel, ConfigDict, Field

from app import spec
from app.data.models import Medium, Playlist, Track
from app.errors import NotFound

tracks = Blueprint("tracks", __name__)


class TrackIn(BaseModel):
    book_id: int
    current_page: int = 1
    medium: Medium = Medium.physical


class TrackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    current_page: int
    medium: Medium | None
    book_id: int


@tracks.get("")
@login_required
def list_tracks(playlist_id: int):
    """List all tracks of a playlist."""
    playlist = Playlist.get_one(
        Playlist.id == playlist_id, Playlist.user_id == current_user.id
    )
    if playlist is None:
        raise NotFound(f"No Playlist found with id: {playlist_id}")

    return {
        "tracks": [TrackOut.model_validate(t).model_dump() for t in playlist.tracks]
    }


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

    return TrackOut.model_validate(track).model_dump(), 200


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
    return TrackOut.model_validate(track).model_dump(), 201


@tracks.delete("/<int:track_id>")
@login_required
def delete_track(playlist_id: int, track_id: int):
    if not Track.delete_by_id(track_id):
        raise NotFound

    return "", 204


class TrackProgressIn(BaseModel):
    pages: int = Field(
        examples=[50],
        description="Takes the current page of the track and adds the provied pages (e.g., 101 + 50)",
    )


@tracks.post("/<int:track_id>/progress")
@login_required
@spec.validate(json=TrackProgressIn)
def add_progress(playlist_id: int, track_id: int, json: TrackProgressIn):
    """Adds progress to a track"""
    track = Track.get_owned_track(playlist_id, track_id, current_user.id)
    if not track:
        raise NotFound(
            f"Track not found track id: {track_id} in playlist id: {playlist_id}"
        )

    new_current_page = track.current_page + json.pages
    track.update(current_page=max(1, new_current_page))

    return TrackOut.model_validate(track).model_dump(), 200
