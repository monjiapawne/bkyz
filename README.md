# bkyz

## Backend

```sh
cd frontend
uv venv
source .venv/bin/activate
uv sync

# Run
flask run

# Test
uv sync --group=test
pytest
```

## Frontend

```sh
cd backend
npm run dev
```

## Links

- http://localhost:5000/api/docs
- http://localhost:5173/
