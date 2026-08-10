from flask import Blueprint

api = Blueprint("api", __name__)

from app.api.books import bp as books_bp

api.register_blueprint(books_bp, url_prefix="/books")
