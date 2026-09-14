import requests


class BookClient:
    def __init_subclass__(cls, headers: dict[str, str], **kw):
        super().__init_subclass__(**kw)
        cls._headers = headers

    def __init__(self, session: requests.Session | None = None, timeout: float | None = None):
        self.s = session or requests.Session()
        self.s.headers.update(self._headers)
        self.timeout = timeout or 5.0
