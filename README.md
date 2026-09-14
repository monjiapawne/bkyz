<img src="docs/booktracker.svg" alt="logo" width="200" align="left">

**bkyz** track your reading progress!

*Built with Flask, Angular and SQLAlchemy.*

<br clear="left">

## Deployment

Requirements: `docker` / `docker-compose`

```sh
cd docker
cp template.env .env
# Update SECRET_KEY in .env - runtime if you don't (security)
docker-compose up -d # Build and start all containers
```
## Local Dev

```sh
cd api && flask db upgrade && flask run
# http://localhost:5000

cd ui && ng serve
# http://localhost:4200
```

Swagger docs at `<flask-endpoint>/api/docs` when `DEBUG` is enabled.

## Tests

```sh
cd api
pytest
```