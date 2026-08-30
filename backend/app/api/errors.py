from app.data.errors import DuplicateError, NotFoundError


class APIError(Exception):
    def __init__(self, message: str, status: int | None = None):
        self.message = message
        if status is not None:
            self.status = status


class BadRequest(APIError):
    def __init__(self, message: str):
        super().__init__(message, 400)


class AuthenticationError(APIError):
    def __init__(self, message: str):
        super().__init__(message, 401)


class Forbidden(APIError):
    def __init__(self, resource: str):
        super().__init__(f"access to {resource} is forbidden", 403)


class NotFound(APIError):
    def __init__(self, resource: str = "resource", value: int | str | None = None):
        msg = []
        msg.append(resource)
        if value:
            msg.append(str(value))
        msg.append("not found")

        super().__init__(" ".join(msg), 404)


class ValidationFailed(APIError):
    status = 422


def register_error_handlers(app):
    """Top level error wrapper, these are what catch errors and format them for http clients."""

    @app.errorhandler(Exception)
    def handle_server_error(e: Exception):
        return {"error": "internal server error"}, 500

    @app.errorhandler(NotFoundError)
    def handle_not_found(e: NotFoundError):
        err = NotFound(e.field, e.value)
        return {"error": err.message}, err.status

    @app.errorhandler(DuplicateError)
    def handle_duplicate(e: DuplicateError):
        return {"error": e.field}, 409

    @app.errorhandler(APIError)
    def handle_api_error(e: APIError):
        return {"error": e.message}, e.status


#     @app.errorhandler(HTTPException)
#     def handle_http_error(e: HTTPException):
#         return {"error": e.description}, e.code
