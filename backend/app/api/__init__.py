from flask import Blueprint

api = Blueprint("api", __name__)

from app.api.books import books as books_bp

api.register_blueprint(books_bp, url_prefix="/books")

from app.api.users import users as user_bp

api.register_blueprint(user_bp, url_prefix="/user")

from app.api.shelves import shelves as shelves_bp

api.register_blueprint(shelves_bp, url_prefix="/shelves")
