import logging
from dataclasses import dataclass, field
from functools import wraps

import requests

from app.data.models import FetchStatus

logger = logging.getLogger("svc")


def fetch_result(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        status = FetchStatus.ok
        res = {}

        try:
            res = func(*args, **kwargs)
        except requests.exceptions.ConnectionError:
            status = FetchStatus.unreachable
        except requests.exceptions.Timeout:
            status = FetchStatus.timeout
        except (requests.exceptions.JSONDecodeError, KeyError, IndexError):
            status = FetchStatus.invalid_format
        except FetchError as e:
            status = e.status

        res = FetchResult(status, res)

        if not res.ok:
            logger.warning(f"{func.__qualname__} -> {res.status}")

        return res

    return wrapper


class FetchError(Exception):
    status = FetchStatus.unknown


class NotFoundError(FetchError):
    status = FetchStatus.not_found


@dataclass
class FetchResult:
    """Helper for external fetches to"""

    status: FetchStatus
    dict_: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == FetchStatus.ok
