from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from spectree import SpecTree
from sqlalchemy import MetaData

from app.errors import reshape_validation

# Used by sqlalchemy to auto name contraints.
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()
login_manager = LoginManager()
spec = SpecTree(
    "flask",
    title="bkyz API",
    version="0.1.0",
    path="api/docs",
    naming_strategy=lambda m: m.__name__,
    before=reshape_validation,
)
