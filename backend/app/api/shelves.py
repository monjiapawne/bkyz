from flask import Blueprint
from flask_login import current_user, login_required
from pydantic import BaseModel, Field, model_validator

from app import spec
from app.errors import NotFound
from app.models import Shelf

shelves = Blueprint("shelves", __name__)


@shelves.get("")
@login_required
def get_all_shelves():
    """Get all shelves of the logged in user."""
    shelves = Shelf.get_all(Shelf.user_id == current_user.id)
    return [s.to_json() for s in shelves]


class ShelfIn(BaseModel):
    name: str | None = Field(None, examples=["Future"])
    description: str | None = Field(None, examples=["Future books I'll read..."])

    @model_validator(mode="after")
    def validate_name(self):
        if self.name is None:
            # This should should check the db and make a logic name
            # like, Page 1. For now just simple.
            self.name = "Unnamed"
        return self


@shelves.post("")
@login_required
@spec.validate(json=ShelfIn)
def add_shelf(json: ShelfIn):
    """Adds a new shelf to the logged user."""
    shelf = Shelf.create(name=json.name, description=json.description, user_id=current_user.id)
    return shelf.to_json(), 201


@shelves.delete("<int:shelf_id>")
@login_required
def delete_shelf(shelf_id: int):
    """Delete a shelf."""
    if not Shelf.delete_by_id(shelf_id):
        raise NotFound(f"No shelf found with id: {shelf_id}")
    return "", 204
