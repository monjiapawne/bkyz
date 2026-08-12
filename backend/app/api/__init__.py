from flask import Blueprint

api = Blueprint("api", __name__)

from app.api.auth import auth as auth_bp
from app.api.books import books as books_bp

api.register_blueprint(books_bp, url_prefix="/books")
api.register_blueprint(auth_bp, url_prefix="/auth")
