import logging

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from spectree import SpecTree
from sqlalchemy import MetaData

from .errors import APIError

# Disable logging of requests like: 127.0.0.1 - - [08/Aug/2026 10:13:40] "GET /api/v1/books/ HTTP/1.1" 200 -
logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# auto name all constraints
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()
spec = SpecTree("flask", title="bkyz API", version="0.1.0", path="api/docs")


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    @app.errorhandler(APIError)
    def handle_api_error(e: APIError):
        return {"error": e.message}, e.status

    from app.api import api

    app.register_blueprint(api, url_prefix="/api/v1")
    if app.config["DEBUG"]:
        spec.register(app)

    return app
