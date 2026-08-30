from flask import Blueprint
from flask_login import current_user, login_required
from pydantic import BaseModel, ConfigDict, Field

from app import spec
from app.api.schemas import Out
from app.data.models import Book, Medium, Playlist, Track
from app.errors import Forbidden, NotFound

tracks = Blueprint("tracks", __name__)


class TrackIn(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    book_id: int = Field(examples=["1"])
    position: int = 1
    """User's progress in the book, consider this their bookmark or current page"""
    unit: str | None = Field("pages", examples=["chapters"])
    """Unit is the string representation of the users progress (e.g., pages, chapters, percent)"""
    total: int | None = Field(None, examples=[24])
    """Total number of unit, if none is provided, it will be inherited from the book"""
    medium: Medium = Medium.physical


class TrackOut(Out):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    unit: str
    total: int
    medium: Medium
    book_id: int


@tracks.get("")
@login_required
def list_tracks(playlist_id: int):
    """List all tracks of a playlist."""
    playlist = Playlist.get_one(Playlist.id == playlist_id, Playlist.user_id == current_user.id)
    if playlist is None:
        raise NotFound(f"No Playlist found with id: {playlist_id}")

    return {"tracks": [TrackOut.json(t) for t in playlist.tracks]}


@tracks.get("/<int:track_id>")
@login_required
def get_track(playlist_id: int, track_id: int):
    """Get a track."""
    track = Track.get_one(
        Track.id == track_id,
        Track.playlist_id == playlist_id,
    )

    if not track:
        raise NotFound(f"Track id: {track_id} was not found in Playlist id: {playlist_id}")
    if not track.verify_track_owner(current_user.id):
        raise Forbidden("track")

    return TrackOut.json(track), 200


@tracks.post("")
@login_required
@spec.validate(json=TrackIn)
def create_track(playlist_id: int, json: TrackIn):
    """Creates a track and adds it to the parent playlist."""
    # Ensure playlist exists
    playlist = Playlist.get_one(
        Playlist.id == playlist_id,
        Playlist.user_id == current_user.id
    )  # fmt: skip
    if playlist is None:
        raise NotFound(f"playlist: {playlist_id} not found")

    book = Book.get_by_id(json.book_id)
    if book is None:
        raise NotFound(f"book: {json.book_id} not found")

    track = Track.create(
        position=json.position,
        unit=json.unit,
        total=json.total if json.total is not None else book.pages,
        medium=json.medium,
        playlist_id=playlist_id,
        book_id=json.book_id,
    )  # fmt: skip

    return TrackOut.json(track), 201


@tracks.delete("/<int:track_id>")
@login_required
def delete_track(playlist_id: int, track_id: int):
    """Delete a track."""
    # validate
    if not Track.delete_by_id(track_id):
        raise NotFound(f"track: {track_id} not found")

    return "", 204


class TrackPatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_id: int | None = None
    unit: str | None = None
    total: int | None = None
    medium: Medium | None = None


@tracks.patch("/<int:track_id>")
@login_required
@spec.validate(json=TrackPatch)
def update_track(playlist_id: int, track_id: int, json: TrackPatch):
    track = Track.get_by_id(track_id)
    if not track:
        raise NotFound(f"track: {track_id} not found")

    changes = json.model_dump(exclude_unset=True, exclude_none=True)
    track.update(**changes)

    return TrackOut.json(track)


class TrackProgressIn(BaseModel):
    position: int = Field(
        examples=[50],
        description="Takes the current page of the track and adds the provied pages (e.g., 101 + 50)",
    )


@tracks.post("/<int:track_id>/progress")
@login_required
@spec.validate(json=TrackProgressIn)
def add_progress(playlist_id: int, track_id: int, json: TrackProgressIn):
    """Adds progress to a track"""
    track = Track.get_by_id(track_id)
    if not track:
        raise NotFound(f"Track not found track id: {track_id} in playlist id: {playlist_id}")

    if not track.verify_track_owner(current_user.id):
        raise Forbidden("track")

    new_pos = track.position + json.position
    track.update(position=max(1, new_pos))

    return TrackOut.json(track), 200
