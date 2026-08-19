class APIError(Exception):
    def __init__(self, message: str, status: int | None = None):
        self.message = message
        if status is not None:
            self.status = status


class BadRequest(APIError):
    status = 400


class AuthenticationError(APIError):
    status = 401


class NotFound(APIError):
    status = 404


class ValidationFailed(APIError):
    status = 422
