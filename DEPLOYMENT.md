# AbleConnect deployment preparation

This repository is prepared for a separate FastAPI service on Render and a static React/Vite frontend on Vercel. **No deployment is performed by this change.** Render's Blueprint has automatic deploys disabled. A Render persistent disk requires a paid web service; the included `render.yaml` uses a paid service tier and a small persistent disk. Review provider pricing and storage needs before creating services. [Render Blueprint reference](https://render.com/docs/blueprint-spec), [Render persistent disks](https://render.com/docs/disks).

## Production environment variables

### Render API service

| Variable | Required value |
|---|---|
| `ENVIRONMENT` | `production` |
| `JWT_SECRET_KEY` | Random secret with at least 32 bytes of entropy. Blueprint generates a 256-bit value; never commit it. |
| `DATABASE_URL` | Render PostgreSQL internal connection string. SQLite is rejected in production. |
| `CORS_ORIGINS` | Comma-separated exact HTTPS Vercel production/custom origins. No wildcard or trailing paths. |
| `CERTIFICATES_STORAGE_DIR` | Path inside the attached private persistent disk, e.g. `/var/data/certificates`. |
| `SEED_DEMO_DATA` | `false` |
| `AUTO_CREATE_SCHEMA` | `false` |

The Render pre-deploy command applies Alembic migrations. Confirm the migration completed before starting the service. Run the first administrator bootstrap from the authorized Render shell after migrations with `python -m app.admin create --email <address> --name <name>`; the password is prompted without echo. There is no public signup or admin-creation endpoint. Rotate the generated JWT secret if it is exposed; changing it invalidates existing sessions.

### Vercel frontend

Set `VITE_API_URL` to the deployed API base URL including `/api`, for example `https://ableconnect-api.onrender.com/api`, in Vercel's Production, Preview, and Development environments as applicable. Set project root to `frontend`; Vercel reads `frontend/vercel.json`. Vite refuses a production build without this URL. [Vercel Vite guide](https://vercel.com/docs/frameworks/frontend/vite), [Vercel environment variables](https://vercel.com/docs/environment-variables).

## Local development

1. Copy `backend/.env.example` to `backend/.env` and replace `JWT_SECRET_KEY` with the output of `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
2. Set `SEED_DEMO_DATA=true` and `AUTO_CREATE_SCHEMA=true` only for a disposable local database if demo personas are needed.
3. Copy `frontend/.env.example` to `frontend/.env.local` for Vite local development.
4. Run the API from `backend` and the frontend from `frontend`.

## Release checklist

- [ ] Review Render/Vercel plans and set billing limits; create the Render PostgreSQL service and private persistent disk.
- [ ] Set all production variables above. Use only the Vercel frontend origin in `CORS_ORIGINS`.
- [ ] Ensure demo seeding and automatic schema creation remain disabled in production.
- [ ] Run `python -m alembic upgrade head` and verify the API `/api/health` check.
- [ ] Bootstrap the first admin from the authorized service shell; then provision all other users through a controlled operator process.
- [ ] Provision synthetic teacher/student/guardian accounts through that reviewed operator process. Production seeding is disabled and the app has no user-provisioning UI/API.
- [ ] Set `VITE_API_URL` in Vercel and run a production build. Vercel must build with this variable set.
- [ ] Check that `.env`, database files, private certificates, and local test storage are ignored by Git.
- [ ] Verify guardian-child and teacher-class grants with dedicated production-like test accounts before real student data is entered.
- [ ] Configure database backups, certificate disk backups, retention, and restoration procedures.
- [ ] Configure account invitation/reset workflows, login throttling, monitoring, incident response, and security review. These are not included in the current application.
- [ ] Perform a privacy, accessibility, and penetration review before any real disability or student data is uploaded.

## Known limitations

Certificate upload validates extension, MIME type, size, and basic file signatures, and stores bytes outside public assets. It does not perform antivirus scanning, PDF/JPEG/PNG parser hardening, or remote object-store encryption/key lifecycle management. The Render disk path is private to the service, but deployment operators must configure and test encrypted backups and access controls.

The current backend has no rate limiting, password reset/invitation flow, account lockout, or full deployment operations/audit tooling. A production deployment remains blocked until those operational controls and all release checks are addressed.
