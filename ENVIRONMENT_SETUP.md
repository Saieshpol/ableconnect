# AbleConnect: Environment Setup Guide

Follow this guide to run AbleConnect in local development or production environments.

---

## 1. System Requirements

- **Operating System:** Windows 10/11, macOS 12+, or Ubuntu 20.04+
- **Python:** 3.10 to 3.13
- **Node.js:** v18.0.0 or higher
- **npm:** v9.0.0 or higher
- **Browser:** Chromium-based browser (Chrome, Edge, Brave), Firefox, or Safari for native Web Speech API support.

---

## 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (cmd):
.\venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run seed script to populate sample data
python -m app.seed

# Start backend server
uvicorn app.main:app --reload --port 8000
```

Verify backend:
- Health check: `http://localhost:8000/api/health`
- Swagger API Docs: `http://localhost:8000/docs`

---

## 3. Frontend Setup

```bash
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```

Open browser at `http://localhost:5173`.

---

## 4. Environment Variables Configuration

### Backend (`backend/.env`)
```env
APP_NAME=AbleConnect
ENVIRONMENT=development
DATABASE_URL=sqlite:///./ableconnect.db
JWT_SECRET_KEY=ableconnect-super-secure-dev-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://127.0.0.1:5173"]
GEMINI_API_KEY="" # Optional: activates AI instruction simplifier if provided; rule-based fallback active by default
```

### Frontend (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000/api
```
