from flask import Blueprint, current_app

api = Blueprint("api", __name__)


@api.get("version")
def api_version():
    # todo: dynamic
    version = current_app.config["GIT_COMMIT"]
    return {"version": version}


from bkyz.api.books import books as books_bp
from bkyz.api.labels import labels as label_bp
from bkyz.api.playlists import playlist as playlists_bp
from bkyz.api.tracks import tracks as tracks_bp
from bkyz.api.users import users as user_bp

api.register_blueprint(user_bp, url_prefix="/user")
api.register_blueprint(books_bp, url_prefix="/books")
api.register_blueprint(playlists_bp, url_prefix="/playlists")
playlists_bp.register_blueprint(tracks_bp, url_prefix="/<int:playlist_id>/tracks")
api.register_blueprint(label_bp, url_prefix="/labels")
