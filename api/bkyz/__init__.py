import logging
import os
from pathlib import Path

from flask import Flask
from spectree.metadata import FunctionDecorator

from bkyz import auth  # noqa: F401 (register the flask-login callback)
from bkyz.api import api
from bkyz.errors import register_error_handlers
from bkyz.extensions import db, login_manager, migrate, spec

# Disable logging of requests like:
# 127.0.0.1 - - [08/Aug/2026 10:13:40] "GET /api/v1/books/ HTTP/1.1" 200
logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("alembic").setLevel(logging.WARNING)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "info").upper(),
    format="%(asctime)s [%(name)s] %(levelname)s : %(message)s",
)
logger = logging.getLogger(__name__)


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or os.environ.get("APP_CONFIG", "config.Config"))
    key = app.config["SECRET_KEY"]
    if app.config["STRICT"] and (not key or key.startswith("please_change_me")):
        raise RuntimeError("SECRET_KEY must be set in production")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    register_error_handlers(app)
    config_covers(app)

    app.register_blueprint(api, url_prefix="/api/v1")
    config_docs(app)  # must be after blueprints are registered

    logger.info(f"* started bkyz-api - commit version: {app.config['GIT_COMMIT']}")
    return app


def config_docs(app):
    """Register API docs, grouping endpoints by blueprint."""
    if not app.config.get("ENABLE_DOCS"):
        return

    for endpoint, view in app.view_functions.items():
        bp = app.blueprints.get(endpoint.rpartition(".")[0])
        if bp:
            # routes without @spec.validate have no metadata yet
            meta = spec.get_function_metadata(view) or spec._function_metadata.setdefault(
                view, FunctionDecorator()
            )
            meta.tags = [bp.name]
    spec.register(app)
    app.add_url_rule("/api/docs", "docs", app.view_functions["openapi_api/docs_swagger"])


def config_covers(app):
    covers = Path(app.config.get("COVERS_DIR") or Path(app.instance_path) / "covers")
    covers.mkdir(parents=True, exist_ok=True)
    app.config["COVERS_DIR"] = covers

    placeholder = Path(app.root_path).parent / "assets" / "placeholder.jpg"
    if not placeholder.is_file():
        app.logger.warning(f"missing cover placeholder at {placeholder}")
    app.config["PLACEHOLDER_COVER"] = placeholder
