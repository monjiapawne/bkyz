from os import environ as env

bind = f":{int(env.get('PORT', '8000'))}"
workers = int(env.get("WORKERS", "4"))

accesslog = "-" if env.get("ACCESS_LOG") == "true" else None
loglevel = env.get("LOG_LEVEL", "info")
