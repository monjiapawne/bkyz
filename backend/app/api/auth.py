from flask import Blueprint
from flask_login import login_user
from pydantic import BaseModel, Field

from app import db, spec
from app.errors import APIError, AuthenticationError
from app.models import User

auth = Blueprint("auth", __name__)


class LoginIn(BaseModel):
    username: str
    password: str
    remember_me: bool = False


@auth.post("/login")
@spec.validate(json=LoginIn)
def login(json: LoginIn):
    user = User.get_user(json.username)
    if not user or not user.verify_password(json.password):
        raise AuthenticationError("Invalid username or password", 401)

    login_user(user, json.remember_me)
    return {"id": user.id, "username": user.username}, 200


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)


@auth.post("/register")
@spec.validate(json=RegisterIn)
def register(json: RegisterIn):
    if User.get_user(json.username):
        raise APIError("Username already taken", 409)

    user = User(
        username=json.username,
        password=json.password,
    )
    db.session.add(user)
    db.session.commit()

    return user.to_json(), 201
