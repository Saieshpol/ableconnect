# AbleConnect Development Progress

## Phase status

| Phase | Status |
|---|---|
| 1. Foundation and portals | Implemented; production frontend build passes |
| 2. Student management and profiles | Existing coverage is partial; not expanded in this hardening pass |
| 3. AAC and messaging | Existing coverage is partial; authorization tightened |
| 4. Teacher tools and progress | Existing coverage is partial; authorization tightened |
| 5. Guardian workflows | Existing coverage is partial; child access is scoped |
| 6. AI and personalization | Not verified in this pass |
| 7. Security, tests, and deployment prep | Hardening completed with remaining blockers below |

## Production security hardening

- [x] Removed `/api/auth/demo-switch`; role tokens are issued only after valid password login.
- [x] JWT secret is required from the environment; production validation requires a 256-bit-length secret and rejects the previous fallback.
- [x] Demo seeding and schema auto-creation default off and are rejected in production.
- [x] Demo persona shortcuts are local-development-only; the production bundle contains no demo passwords.
- [x] Added shell-only administrator bootstrap; there is no public signup/admin-creation route.
- [x] Scoped student/class lists, profiles, requests, messages, schedules, and metrics by role and authorized relationships.
- [x] Certificate uploads require an authorized guardian and validate size, extension, MIME type, and basic file signature. Files remain outside public assets and download routes enforce authorization.
- [x] Production CORS requires explicit HTTPS origins; wildcard origins are rejected.
- [x] Frontend uses `VITE_API_URL`; Vite refuses a production build when it is missing.
- [x] Added an Alembic baseline, Render Blueprint, Vercel config, deployment checklist, and Git ignores for secrets, database files, and private certificate storage.

## Verification

- Frontend production build with `VITE_API_URL`: passed (`tsc` and Vite).
- Production bundle scan for demo passwords, `localhost:8000`, and `/auth/demo-switch`: no matches.
- Backend security/authorization tests: **24 passed**.
- Alembic migration upgrade and `alembic check` on isolated SQLite DB: passed; no schema drift.
- Production-configured FastAPI ASGI startup and `/api/health`: passed.
- A live Render PostgreSQL connection, Render disk persistence, and hosted migrations were not verified because no Render services exist in this workspace.

## Remaining deployment blockers

- Push this workspace to a Git remote and link it to Vercel/Render.
- Create the Render PostgreSQL service and paid persistent disk; set the exact Vercel HTTPS origin in `CORS_ORIGINS`.
- Configure `VITE_API_URL` in Vercel to the deployed Render API.
- Bootstrap the first administrator from the authorized Render shell after migrations.
- Provision synthetic teacher/student/guardian accounts through a reviewed operator process; production seeding remains off and no user-provisioning UI/API is present.
- Complete operational safeguards still missing from the app: login throttling, password reset/invitation lifecycle, antivirus/content parser scanning, backup restore testing, and a privacy/security review before entering real student data.

**Status: deployment prepared, not production-ready and not deployed.**
