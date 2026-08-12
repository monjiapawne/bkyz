from flask import Blueprint
from flask_login import login_user
from pydantic import BaseModel
from sqlalchemy import select

from app import db, spec
from app.errors import AuthenticationError
from app.models import User

auth = Blueprint("auth", __name__)


class LoginIn(BaseModel):
    username: str
    password: str
    remember_me: bool = False


@auth.post("/login")
@spec.validate(json=LoginIn)
def login(json: LoginIn):
    user = db.session.scalar(select(User).where(User.username == json.username))

    if user is not None and user.verify_password(json.password):
        login_user(user, json.remember_me)
        return {"id": user.id, "username": user.username}, 200

    raise AuthenticationError("Invalid username or password", 401)
