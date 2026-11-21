import pytest
import requests


@pytest.fixture(autouse=True)
def no_network(request, monkeypatch):
    """Block real HTTP unless test is marked by @pytest.mark.network"""

    if request.node.get_closest_marker("network"):
        return

    def blocked(*args, **kwargs):
        raise requests.exceptions.ConnectionError("network disabled in tests")

    monkeypatch.setattr(requests.Session, "send", blocked)
