import logging
from typing import TYPE_CHECKING

from flask_login import UserMixin
from sqlalchemy import (
    String,
    false,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.data.base import CRUDMixin

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.data.playlist import Playlist


class User(CRUDMixin, UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=false())

    playlists: Mapped[list["Playlist"]] = relationship(back_populates="user")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
