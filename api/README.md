# bkyz API

## Setup

```sh
cd api
uv sync

# Upgrade database
uv run flask db upgrade

# Run
uv run flask run

# Test
uv run pytest # run tests that don't require network
uv run pytest -m network # run tests that require network
uv run pytest -m 'network or not network' # run all
```

## New migration

```sh
uv run flask db migrate -m "{name}"
uv run flask db upgrade
```
