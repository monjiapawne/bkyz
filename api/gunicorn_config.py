from os import environ as env


def _str_to_bool(value: str | None) -> bool:
    return value is not None and value.strip().lower() in ("true", "1")


# Config for gunicorn. This file is somewhat a helper to make environment variables
# have sensible defaults and move the weight to here rather than in the .env
# ref: https://gunicorn.org/reference/settings/#access_log_format

# Performance
workers = int(env.get("WORKERS", "4"))

# Config
bind = f":{int(env.get('PORT', '8000'))}"

# Logging
accesslog = "-" if _str_to_bool(env.get("ACCESS_LOG", "")) else None
loglevel = env.get("LOG_LEVEL", "info")
