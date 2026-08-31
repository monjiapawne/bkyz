class NotFoundError(Exception):
    def __init__(self, field: str, value):
        self.field = field
        self.value = value


class DuplicateError(Exception):
    def __init__(self, field: str = "", value=None):
        self.field = field
        self.value = value
