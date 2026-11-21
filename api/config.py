import os


def _str_to_bool(value: str | None) -> bool:
    return value is not None and value.strip().lower() in ("true", "1")


class Config:
    # Read from env
    SECRET_KEY = os.getenv("SECRET_KEY", "please_change_me_only_for_dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///bkyz.db")
    COVERS_DIR = os.getenv("COVERS_DIR")
    TIMEZONE = os.getenv("TIMEZONE", "UTC")
    GIT_COMMIT = os.getenv("GIT_COMMIT", "unknown")

    # Defaults testing/prod overide some
    STRICT = False  # True: refuse to start with dev SECRET KEY
    ENABLE_DOCS = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite://")


class ProdConfig(Config):
    STRICT = True
    ENABLE_DOCS = _str_to_bool(os.getenv("ENABLE_DOCS", "false"))
    SESSION_COOKIE_SECURE = True
