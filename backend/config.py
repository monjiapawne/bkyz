import os


class Config:
    STRICT = False
    DEBUG = False
    ENABLE_DOCS = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///bkyz.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "please_change_me_only_for_dev")
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    CORS_ALLOW_LIST = ()
    # COVERS_DIR is the path to store the book covers, defaults to /instances/covers
    COVERS_DIR = os.environ.get("COVERS_DIR")


class DevConfig(Config):
    DEBUG = True
    CORS_ALLOW_LIST = ("http://localhost:4200", "http://127.0.0.1:4200")
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    PROPAGATE_EXCEPTIONS = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", "sqlite://"
    )  # in memory sqlite for testing


class LocalConfig(Config):
    STRICT = False
    SESSION_COOKIE_SECURE = True
    CORS_ALLOW_LIST = ("http://localhost:8080", "http://localhost:4200")


class ProdConfig(Config):
    STRICT = True
    ENABLE_DOCS = False
    SESSION_COOKIE_SECURE = True
    CORS_ALLOW_LIST = tuple(
        origin for origin in os.environ.get("CORS_ALLOW_LIST", "").split(",") if origin
    )
