import pytest

from app.models import User


def test_password_no_getter():
    u = User(password="cat")
    with pytest.raises(AttributeError):
        _ = u.password


def test_password_verification():
    u = User(password="cat")
    assert u.verify_password("cat")
    assert not u.verify_password("dog")
