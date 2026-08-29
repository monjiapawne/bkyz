

<img src="docs/booktracker.svg" alt="logo" width="200" align="left">

**bkyz** track your reading progress!

*Built with Flask, Angular and SQLAlchemy.*

<br clear="left">

## Usage


## Backend

```sh
# Setup
cd backend
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

## Frontend

```sh
cd frontend
npm run dev
```

## Links

- http://localhost:5000/api/docs
- http://localhost:5173/
