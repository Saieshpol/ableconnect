# Vercel deployment

The Vite frontend is configured in `frontend/vercel.json`. Set the Vercel project root to `frontend`. Add `VITE_API_URL` before creating a production build:

```text
VITE_API_URL=https://<your-hosted-api>/api
```

The API must be deployed separately with PostgreSQL and private persistent certificate storage. `VITE_API_URL` is mandatory for production builds; local development uses `frontend/.env.example`.

Use [DEPLOYMENT.md](DEPLOYMENT.md) for the Render Blueprint, full variable checklist, and remaining production blockers. Do not deploy until its release checklist is complete.
