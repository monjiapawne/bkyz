from functools import wraps

from flask_login import current_user

from bkyz.errors import ForbiddenError


def admin_required(func):
    """Protect a route for admin only."""

    @wraps(func)
    def verify_admin(*args, **kwargs):
        if not current_user.is_admin:
            raise ForbiddenError

        return func(*args, **kwargs)

    return verify_admin
