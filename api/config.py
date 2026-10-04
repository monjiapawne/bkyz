import os


def _str_to_bool(value: str) -> bool:
    """Converts a string to a bool."""
    return value.lower().strip() in ("true", "1")


class Config:
    STRICT = False
    PROPAGATE_EXCEPTIONS = False
    ENABLE_DOCS = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    CORS_ALLOW_LIST = "http://localhost:4200"

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///bkyz.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "please_change_me_only_for_dev")
    # COVERS_DIR is the path to store the book covers, defaults to /instances/covers
    COVERS_DIR = os.getenv("COVERS_DIR")
    TIMEZONE = os.getenv("TIMEZONE", "UTC")


class TestingConfig(Config):
    TESTING = True
    PROPAGATE_EXCEPTIONS = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL", "sqlite://"
    )  # in memory sqlite for testing


class ProdConfig(Config):
    STRICT = True
    ENABLE_DOCS = _str_to_bool(os.getenv("ENABLE_DOCS", "false"))
    SESSION_COOKIE_SECURE = True
    CORS_ALLOW_LIST = tuple(
        origin for origin in os.getenv("CORS_ALLOW_LIST", "").split(",") if origin
    )
