from app.data import User
from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    return {"error": "authentication required"}, 401
