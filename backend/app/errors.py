class APIError(Exception):
    def __init__(self, message: str, status: int | None = 400):
        self.message = message
        self.status = status


class NotFound(APIError):
    status = 404
