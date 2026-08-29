class APIError(Exception):
    def __init__(self, message: str, status: int | None = None):
        self.message = message
        if status is not None:
            self.status = status


class BadRequest(APIError):
    status = 400


class AuthenticationError(APIError):
    status = 401


class Forbidden(APIError):
    def __init__(self, resource: str):
        super().__init__(f"access to {resource} is forbidden", 403)


class NotFound(APIError):
    status = 404


class ValidationFailed(APIError):
    status = 422
