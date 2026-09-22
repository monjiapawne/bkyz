import logging

from flask import request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger("api")


class BkyzError(Exception):
    """Base class for every exception bkyz raises."""

    status = 500


class BadRequestError(BkyzError):
    status = 400


class UnauthorizedError(BkyzError):
    status = 401


class ForbiddenError(BkyzError):
    status = 403

    def __init__(self, resource: str = "resource") -> None:
        super().__init__(f"access to {resource} is forbidden")


class NotFoundError(BkyzError):
    status = 404

    def __init__(self, resource: str = "resource", value: int | str | None = None):
        msg = [resource]
        if value:
            msg.append(str(value))
        msg.append("not found")

        super().__init__(" ".join(msg))


class ResourceExistsError(BkyzError):
    status = 409

    def __init__(self, resource: str = "resource") -> None:
        super().__init__(f"{resource} already exists")


def register_error_handlers(app):
    """Top level error wrapper, these are what catch errors and format them for http clients."""

    @app.errorhandler(BkyzError)
    def handle_bkyz_error(e: BkyzError):
        """Catch expected errors"""
        logger.info(f"{e.status} -> {request.method} {request.path}: {e}")
        if app.config["DEBUG"]:
            raise e
        return {"error": str(e)}, e.status

    @app.errorhandler(HTTPException)
    def handle_http_error(e: HTTPException):
        """Pass through framework errors (404, 405, etc) in json shape"""
        logger.info(f"{e.code} -> {request.method} {request.path}: {e.name}")
        return {"error": e.description}, e.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(e: Exception):
        """Catch unexpected, uncaught errors"""
        logger.exception(f"uncaught error: {request.method}, {request.path}")
        if app.config["DEBUG"]:
            raise e
        return {"error": "internal server error"}, 500
