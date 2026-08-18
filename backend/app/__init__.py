import logging

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from pydantic import ValidationError
from spectree import SpecTree
from sqlalchemy import MetaData
from werkzeug.exceptions import HTTPException

from .errors import APIError

# Disable logging of requests like:
# 127.0.0.1 - - [08/Aug/2026 10:13:40] "GET /api/v1/books/ HTTP/1.1" 200
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
login_manager = LoginManager()


def reshape_validation(req, resp, req_validation_error: ValidationError, instance):
    if req_validation_error:
        err = req_validation_error.errors()[0]  # first failure
        field = err["loc"][-1]
        raise APIError(f"{field}: {err['msg']}", 422)


spec = SpecTree(
    "flask",
    title="bkyz API",
    version="0.1.0",
    path="api/docs",
    naming_strategy=lambda m: m.__name__,
    before=reshape_validation,
)


def create_app(config_object="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)

    config_cors(app)
    config_error_handlers(app)
    config_flask_login(app)

    from app.api import api

    app.register_blueprint(api, url_prefix="/api/v1")

    # must be after blueprints are registered
    config_docs(app)

    return app


def config_docs(app):
    """Register API docs, grouping endpoints by blueprint."""
    if app.config["DEBUG"]:
        for endpoint, view in app.view_functions.items():
            view.tags = (
                [bp.name]
                if (bp := app.blueprints.get(endpoint.rpartition(".")[0]))
                else []
            )
        spec.register(app)
        app.add_url_rule(
            "/api/docs", "docs", app.view_functions["openapi_api/docs_swagger"]
        )


def config_flask_login(app):
    login_manager.init_app(app)
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        return {"error": "authenticated required"}, 401


def config_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(e: APIError):
        return {"error": e.message}, e.status

    @app.errorhandler(HTTPException)
    def handle_http_error(e: HTTPException):
        return {"error": e.description}, e.code

    @app.errorhandler(Exception)
    def handle_server_error(e: Exception):
        app.logger.exception("unhandled exception")
        if app.config["DEBUG"]:
            raise e
        return {"error": "internal server error"}, 500


def config_cors(app):
    CORS(app, supports_credentials=True, origins=app.config.get("CORS_ALLOW_LIST", []))
