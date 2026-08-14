class APIError(Exception):
    def __init__(self, message: str, status: int | None = 400):
        self.message = message
        self.status = status


class BadRequest(APIError):
    status = 400


class AuthenticationError(APIError):
    status = 401


class NotFound(APIError):
    status = 404
