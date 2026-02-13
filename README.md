# Multi-Agent Debate System

A monorepo containing a FastAPI backend and React frontend for an AI debate system.

## Quick Start

### Backend Setup
```bash
cd backend
poetry install
poetry run uvicorn main:app --reload
```

The backend will run on `http://localhost:8000` with a health check at `GET /health`.

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:5173`.

## Development

- **Backend changes**: Edit files in `backend/`. The FastAPI server auto-reloads with `--reload`.
- **Frontend changes**: Edit files in `frontend/src/`. Vite hot-reloads changes.
- **CORS**: The backend allows requests from `http://localhost:5173` (Vite dev port).

See `CLAUDE.md` for detailed architecture and development guidelines.
