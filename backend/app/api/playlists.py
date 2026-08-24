from flask import Blueprint
from flask_login import current_user, login_required
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app import spec
from app.data.models import Playlist
from app.errors import NotFound

playlist = Blueprint("playlists", __name__)


class PlaylistIn(BaseModel):
    name: str | None = Field(None, examples=["Future"])
    description: str | None = Field(None, examples=["Future books I'll read..."])

    @model_validator(mode="after")
    def validate(self):
        if self.name is None:
            # This should should check the db and make a logic name
            # like, Page 1. For now just simple.
            self.name = "Unnamed"
        self.description = self.description or "Empty."
        return self


class PlaylistOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    user_id: int


@playlist.get("")
@login_required
def get_all_playlists():
    """Get all playlists of the logged in user."""
    playlists = Playlist.get_all(Playlist.user_id == current_user.id)
    return [PlaylistOut.model_validate(s).model_dump() for s in playlists]


@playlist.post("")
@login_required
@spec.validate(json=PlaylistIn)
def add_shelf(json: PlaylistIn):
    """Adds a new Playlist to the logged user."""
    playlist = Playlist.create(
        name=json.name, description=json.description, user_id=current_user.id
    )
    return PlaylistOut.model_validate(playlist).model_dump(), 201


@playlist.delete("<int:playlist_id>")
@login_required
def delete_shelf(playlist_id: int):
    """Delete a Playlist."""
    if not Playlist.delete_by_id(playlist_id):
        raise NotFound(f"No Playlist found with id: {playlist_id}")
    return "", 204
