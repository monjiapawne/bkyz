# bkyz

## Setup

```sh
# Setup
cd api
uv venv
uv sync

# Upgrade database
uv run flask db upgrade

# Run
uv run flask run

# Test
uv sync --group=test
uv run pytest # run tests that don't require network
uv run pytest -m network # run test that require network
uv run pytest -m 'network or not network' # run all
```

## Setup Commands

```sh
flask run
flask db migrate -m "{name}"
flask db upgrade

# Nuke db 
rm instance/bkyz.db
rm migrations/versions/*.py
flask db migrate -m "initial schema"
flask db upgrade
```