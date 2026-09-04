import logging

from flask import request

logger = logging.getLogger(__name__)


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
        super().__init__("{resource} already exists")


def register_error_handlers(app):
    """Top level error wrapper, these are what catch errors and format them for http clients."""

    @app.errorhandler(BkyzError)
    def handle_bkyz_error(e: BkyzError):
        """Catch expected errors"""
        return {"error": str(e)}, e.status

    @app.errorhandler(Exception)
    def handle_unexpected_erorr(e: Exception):
        """Catch unexpected, uncaught errors"""
        logger.exception(f"uncaught error: {request.method}, {request.path}")
        if app.config["DEBUG"]:
            raise e
        return {"error": "internal server error"}, 500
