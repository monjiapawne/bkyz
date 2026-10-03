from flask import Blueprint
from flask_login import current_user, login_required
from pydantic import BaseModel, ConfigDict, Field

from app import spec
from app.api.books import BookOut
from app.api.schemas import Out, UTCDatetime
from app.data import Book, Medium, Playlist, Track, TrackProgress
from app.errors import NotFoundError

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
    active: bool = Field(False, examples=[True])
    notes: str | None = Field(None, max_length=255)
    rating: int | None = Field(None, ge=1, le=10, examples=[5])


class TrackOut(Out):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    unit: str
    total: int
    medium: Medium
    book_id: int
    sort_order: int
    active: bool
    notes: str | None
    last_read_at: UTCDatetime | None
    rating: int | None


class TrackFullOut(TrackOut):
    book: BookOut


@tracks.get("")
@login_required
def list_tracks(playlist_id: int):
    """List all tracks of a playlist."""
    playlist = Playlist.get_one(Playlist.id == playlist_id, Playlist.user_id == current_user.id)
    if playlist is None:
        raise NotFoundError("playlist_id", playlist_id)

    return {"tracks": [TrackOut.json_(t) for t in playlist.tracks]}


@tracks.get("/<int:track_id>")
@login_required
def get_track(playlist_id: int, track_id: int):
    """Get a track."""
    return TrackOut.json_(Track.get_owned(track_id, current_user.id)), 200


@tracks.post("")
@login_required
@spec.validate(json=TrackIn)
def create_track(playlist_id: int, json: TrackIn):
    """Creates a track and adds it to the parent playlist."""
    if json.total is None:
        json.total = Book.get_by_id(json.book_id).pages

    track = Track.create(
        playlist_id=playlist_id,
        position=json.position,
        unit=json.unit,
        total=json.total,
        medium=json.medium,
        book_id=json.book_id,
        active=json.active,
        notes=json.notes,
        rating=json.rating,
    )

    return TrackOut.json_(track), 201


@tracks.delete("/<int:track_id>")
@login_required
def delete_track(playlist_id: int, track_id: int):
    """Delete a track."""
    Track.get_owned(track_id, current_user.id).delete()
    return "", 204


class TrackPatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_id: int | None = None
    playlist_id: int | None = None
    position: int | None = None
    unit: str | None = None
    total: int | None = None
    medium: Medium | None = None
    active: bool | None = None
    notes: str | None = None
    rating: int | None = Field(None, ge=1, le=10)
    position_updated_at: UTCDatetime | None = None


@tracks.patch("/<int:track_id>")
@login_required
@spec.validate(json=TrackPatch)
def update_track(playlist_id: int, track_id: int, json: TrackPatch):
    track = Track.get_by_id(track_id)
    changes = json.model_dump(exclude_unset=True)
    if "notes" in json.model_fields_set:
        changes["notes"] = json.notes
    track.update(**changes)

    return TrackOut.json_(track)


class TrackProgressOut(Out):
    from_position: int
    to_position: int
    delta: int
    created_at: UTCDatetime


class TrackProgressIn(BaseModel):
    position: int = Field(examples=[50])


@tracks.post("/<int:track_id>/progress")
@login_required
@spec.validate(json=TrackProgressIn)
def add_progress(playlist_id: int, track_id: int, json: TrackProgressIn):
    """Adds progress to a track"""
    track = Track.get_owned(track_id, current_user.id)
    track.progress_track(json.position)
    return TrackOut.json_(track), 200


@tracks.get("/<int:track_id>/history")
@login_required
def list_track_history(playlist_id, track_id: int):
    track = Track.get_owned(track_id, current_user.id)  # Verify ownership
    return [TrackProgressOut.json_(record) for record in track.progress_log], 200
