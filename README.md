# ResumeAgent

Local AI resume tailoring agent — Next.js frontend, FastAPI backend.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager — installs Python 3.13 automatically)
- Node.js 20+
- Docker & Docker Compose (optional)

### Install uv (recommended — no sudo)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart your shell, or:
source "$HOME/.local/bin/env"
```

## Setup

```bash
cp .env.example .env
# Edit .env — set OPENAI_API_KEY

make install
```

## Run locally

```bash
make dev
```

## Run with Docker

```bash
docker compose up --build
```

## Project layout

See architecture docs in project planning. Key paths:

- `data/inputs/` — master resume and template
- `data/outputs/` — generated tailored resumes and PDFs
- `backend/` — FastAPI application
- `frontend/` — Next.js application
