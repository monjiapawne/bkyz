from flask import Blueprint

api = Blueprint("api", __name__)

from app.api.books import books as books_bp
from app.api.playlists import playlist as playlists_bp
from app.api.tracks import tracks as tracks_bp
from app.api.users import users as user_bp

api.register_blueprint(user_bp, url_prefix="/user")
api.register_blueprint(books_bp, url_prefix="/books")
api.register_blueprint(playlists_bp, url_prefix="/playlists")
playlists_bp.register_blueprint(tracks_bp, url_prefix="/<int:playlist_id>/tracks")
