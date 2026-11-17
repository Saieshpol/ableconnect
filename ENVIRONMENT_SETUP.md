# AbleConnect: Environment Setup

## Local development

Requirements: Python 3.10+, Node.js 18+, and PostgreSQL for deployment. Local development can use SQLite.

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Generate a secret with `python -c "import secrets; print(secrets.token_urlsafe(48))"` and put the result in `JWT_SECRET_KEY` in `backend/.env`. To use local demo data, set `SEED_DEMO_DATA=true` and `AUTO_CREATE_SCHEMA=true`; do this only with a disposable local database. Then run:

```powershell
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
Copy-Item .env.example .env.local
pnpm install
pnpm dev
```

`frontend/.env.example` points to the local API. Production builds require `VITE_API_URL` and reject missing values.

### Tests and migration checks

From `backend`:

```powershell
python -m pytest -q
python -m alembic upgrade head
```

The tests use a temporary SQLite database and local demo fixtures. For a fresh non-test development database, either enable schema auto-creation locally or run Alembic migrations.

## Production

Do not use demo accounts, SQLite, local filesystem uploads, or the development environment file in production. Configure PostgreSQL and a private persistent disk, apply Alembic migrations, provision an administrator through the authorized service shell, and set exact HTTPS CORS origins. Follow [DEPLOYMENT.md](DEPLOYMENT.md) for Render/Vercel setup and the complete environment-variable checklist.
