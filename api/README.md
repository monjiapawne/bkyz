# bkyz

## Setup

```sh
# Setup
cd api
uv venv
source .venv/bin/activate
uv sync

# Upgrade database
flask db upgrade

# Run
flask run

# Test
uv sync --group=test
pytest
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