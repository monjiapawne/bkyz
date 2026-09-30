from functools import wraps

from flask_login import current_user

from app.errors import ForbiddenError, UnauthorizedError


def admin_required(func):
    """Protect a route for admin only."""

    @wraps(func)
    def verify_admin(*args, **kwargs):
        if not current_user.is_authenticated:
            raise UnauthorizedError
        if not current_user.is_admin:
            raise ForbiddenError

        return func(*args, **kwargs)

    return verify_admin
