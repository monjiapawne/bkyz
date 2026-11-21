<img src="docs/bkyz.svg" alt="logo" width="200" align="left">

**bkyz** track your reading progress!

*Built with Flask, Angular and SQLAlchemy.*

<br clear="left">

## Features

- Progress logging of book progress (for analytics)

## Deployment

Requirements: `docker` with `docker compose`

```sh
cd docker
cp template.env .env
# Set SECRET_KEY in .env (the API refuses to start with the default)
docker compose up -d # Build and start all containers
# Access database through docker
docker compose exec db psql -U bkyz
```

## Local Dev

```sh
cd api && uv run flask db upgrade && uv run flask run
# http://localhost:5000

cd ui && ng serve
# http://localhost:4200
```

Swagger docs at `<flask-endpoint>/api/docs` when `ENABLE_DOCS` is enabled.

## Tests

```sh
cd api && uv run pytest
```

See [api/README.md](api/README.md) for network tests.
