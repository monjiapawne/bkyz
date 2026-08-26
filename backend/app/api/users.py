from flask import Blueprint
from flask_login import current_user, login_required, login_user, logout_user
from pydantic import BaseModel, ConfigDict, Field

from app import spec
from app.data.models import User
from app.errors import APIError, AuthenticationError, NotFound
from app.api.schemas import Out

users = Blueprint("users", __name__)


class UserIn(BaseModel):
    username: str
    password: str
    remember_me: bool = False


class UserOut(Out):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


@users.post("/login")
@spec.validate(json=UserIn)
def login(json: UserIn):
    """Login as a user."""
    user = User.get_one(User.username == json.username)
    if not user or not user.verify_password(json.password):
        raise AuthenticationError("Invalid username or password", 401)

    login_user(user, json.remember_me)
    return UserOut.json(user), 200


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
    if User.get_one(User.username == json.username):
        raise APIError("Username already taken", 409)

    user = User.create(
        username=json.username,
        password=json.password,
    )

    return UserOut.json(user), 201


@users.get("<int:user_id>")
def user_info(user_id: int):
    """Get a user's info."""
    user = User.get_one(User.id == user_id)
    if user is None:
        raise NotFound("user not found")

    return UserOut.json(user), 200


@users.get("")
@login_required
def current_user_info():
    """Get the current logged in user's info.

    Userful to ensure your logged in.
    """
    user = User.get_by_id(current_user.id)
    return UserOut.json(user), 200
