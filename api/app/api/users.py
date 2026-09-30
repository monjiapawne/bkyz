import logging

from flask import Blueprint
from flask_login import current_user, login_required, login_user, logout_user
from pydantic import BaseModel, ConfigDict, Field

from app import spec
from app.api.auth import admin_required
from app.api.schemas import Out
from app.data import User
from app.errors import NotFoundError, UnauthorizedError, ForbiddenAsNotFound, ForbiddenError

logger = logging.getLogger(__name__)

users = Blueprint("users", __name__)


class UserIn(BaseModel):
    username: str
    password: str
    remember_me: bool = False


class UserOut(Out):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    is_admin: bool


@users.post("/login")
@spec.validate(json=UserIn)
def login(json: UserIn):
    """Login as a user."""
    user = User.get_one(User.username == json.username)
    if not user or not user.verify_password(json.password):
        raise UnauthorizedError("Invalid username or password")

    login_user(user, json.remember_me)
    return UserOut.json_(user), 200


@users.get("/logout")
def logout():
    """Logout the currently logged in user."""
    logout_user()
    return "", 204


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)


@users.post("/register")
@spec.validate(json=RegisterIn)
def register(json: RegisterIn):
    """Register a user."""
    user = User.create(
        username=json.username,
        password=json.password,
    )

    return UserOut.json_(user), 201


@users.get("<int:user_id>")
@login_required
def user_info(user_id: int):
    """Get a user's info."""
    user = User.get_one(User.id == user_id)
    if user is None:
        raise NotFoundError("user")

    return UserOut.json_(user), 200


@users.get("me")
@login_required
def current_user_info():
    """Get the current logged in user's info.

    Userful to ensure your logged in.
    """
    user = User.get_by_id(current_user.id)
    return UserOut.json_(user), 200


class UserPatch(BaseModel):
    username: str | None = None
    is_admin: bool | None = None
    password: str | None = None


@users.patch("<int:user_id>")
@spec.validate(json=UserPatch)
@login_required
def update_user(json: UserPatch, user_id):
    """Update a user.

    Users can edit their own accounts, admins can edit all accounts.
    """
    if current_user.id != user_id and not current_user.is_admin:
        raise ForbiddenAsNotFound

    changes = json.model_dump(exclude_unset=True)

    if "is_admin" in changes and not current_user.is_admin:
        raise ForbiddenError("is_admin")

    user = User.get_by_id(user_id)

    if "is_admin" in changes and changes["is_admin"] != user.is_admin:
        promo = changes["is_admin"]
        action = "promoted" if promo else "demoted"
        logger.info("user %s %s to admin by %s", user, action, current_user)

    user.update(**changes)
    return UserOut.json_(user)


@users.get("")
@admin_required
def list_users():
    """List all users."""
    return [UserOut.json_(user) for user in User.get_all()], 200
