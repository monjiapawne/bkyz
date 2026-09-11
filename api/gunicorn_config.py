from os import environ as env

# Config for gunicorn. This file is somewhat a helper to make environment variables
# have sensible defaults and move the weight to here rather than in the .env
# ref: https://gunicorn.org/reference/settings/#access_log_format


def strasbool(v: str | None) -> bool:
    if v is None:
        return False
    return v.lower() in ("true", "1")


# Performance
workers = int(env.get("WORKERS", "4"))

# Config
bind = f":{int(env.get('PORT', '8000'))}"

# Logging
accesslog = "-" if strasbool(env.get("ACCESS_LOG")) else None
loglevel = env.get("LOG_LEVEL", "info")
