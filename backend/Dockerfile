FROM python:3.13-alpine AS base

RUN adduser -D bkyz-api -h /home/bkyz-api -s /sbin/nologin -u 65532 bkyz-api

# Setup dir for covers
ENV COVERS_DIR=/data/covers
RUN mkdir -p /data/covers && chown -R bkyz-api:bkyz-api /data
VOLUME [ "/data" ]


# Install uv (to use uv.lock)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
# Install third party depend
RUN uv sync --frozen --no-install-project --no-dev --group deploy --no-cache

COPY app ./app
COPY config.py bkyz.py gunicorn_config.py ./
COPY migrations ./migrations
COPY assets ./assets

RUN uv sync --frozen --no-dev --group deploy --no-cache

USER bkyz-api
ENV FLASK_APP=bkyz
# For uv cache
ENV PATH="/app/.venv/bin:$PATH" 

EXPOSE 8000
CMD ["sh", "-c", "flask db upgrade && gunicorn -c gunicorn_config.py 'bkyz:create_app()'"]