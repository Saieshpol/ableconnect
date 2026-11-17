# AbleConnect

**Tagline:** *Better Understanding. Easier Communication. Inclusive Education.*

AbleConnect is an accessibility-focused educational communication platform foundation designed to support communication between teachers, students, and parents/guardians.

Unlike conventional learning management systems, AbleConnect provides **two-way accessible communication**. Students can communicate their needs, emotions, and questions independently using visual symbol boards (AAC), assistive speech synthesis, and direct help requests, while teachers receive structured individual communication guidelines, support strategies, and instruction simplification tools.

---

## 🌟 Core Highlights

- **Student-Centric Individualization:** No one-size-fits-all assumptions. Every student has an individually configured profile with communication methods, sensory preferences, and approved teacher instructions.
- **Two-Way Visual AAC & Speech Board:** Interactive picture-based communication boards with multi-card sentence builder, Web Speech Synthesis, and direct messaging to teachers.
- **Dignified Student Help Requests:** Fast, non-stigmatizing requests ("I need help", "I need a break", "I don't understand") with clear status tracking (Sent -> Seen -> Responded).
- **Teacher Instruction Simplifier:** AI-assisted and rule-based step-by-step instruction breakdown with text-to-speech and visual readability controls.
- **Visual Timetables & Schedules:** Accessible daily schedules with visual icons and period breakdown.
- **Parent / Guardian Collaboration Portal:** Authorized guardian access to communication preferences, teacher updates, and progress logs.
- **WCAG 2.2 AA Compliance:** High contrast mode, dynamic font scaling, keyboard-first navigation, reduced motion support, screen-reader friendly semantic markup, and touch-optimized interfaces.
- **Robust Privacy & Child Safety:** Strict Role-Based Access Control (RBAC), private teacher observations, audit logging, and no public indexing of sensitive disability information.

---

## 📂 Repository Structure

```
ableconnect/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/              # API Route Handlers
│   │   │   ├── auth.py       # Authentication & JWT tokens
│   │   │   ├── classes.py    # Class & Roster management
│   │   │   ├── students.py   # Student profiles & preferences
│   │   │   ├── communication.py # AAC boards, messages & help requests
│   │   │   ├── tools.py      # Instruction simplifier & schedules
│   │   │   └── guardian.py   # Guardian portal routes
│   │   ├── core/             # Configuration & Security
│   │   │   ├── config.py     # Environment settings
│   │   │   ├── security.py   # Hashing, JWT verification, RBAC
│   │   │   └── database.py   # SQLAlchemy async/sync engine
│   │   ├── models/           # 19 Normalized SQLAlchemy Models
│   │   ├── schemas/          # Pydantic Request/Response models
│   │   ├── services/         # Business logic (AAC, Simplifier, Speech)
│   │   └── seed.py           # Comprehensive seed data for demo
│   ├── requirements.txt      # Python dependencies
│   └── main.py               # Backend entry point
├── frontend/                 # Vite + React + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── components/       # Reusable accessible UI components
│   │   │   ├── common/       # AccessibilityBar, Navbar, Modal, Button
│   │   │   ├── teacher/      # Teacher dashboard cards, student roster
│   │   │   ├── student/      # AAC Board, Help Button, Emotion Check-in
│   │   │   └── guardian/     # Guardian child view & messages
│   │   ├── context/          # AuthContext, AccessibilityContext
│   │   ├── pages/            # LandingPage, TeacherDashboard, StudentDashboard, etc.
│   │   ├── services/         # API clients & Web Speech service
│   │   ├── types/            # TypeScript interfaces matching API schemas
│   │   └── index.css         # Tailwind & Accessibility themes
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── README.md                 # System Overview & Getting Started
├── PROJECT_ARCHITECTURE.md   # Architectural Decisions & Data Flows
├── DATABASE_SCHEMA.md        # Complete 19-table Data Model Specification
├── API_DOCUMENTATION.md      # REST API Endpoints & Payloads
├── DEVELOPMENT_PROGRESS.md   # Phase Tracking & Milestone Completion
├── ENVIRONMENT_SETUP.md      # Installation & Configuration Guide
└── SECURITY_AND_PRIVACY.md   # Child Safety, Privacy & RBAC Policy
```

---

## 🚀 Quick Start

### 1. Prerequisites
- **Node.js**: v18+ (tested on Node v24)
- **Python**: 3.10+ (tested on Python 3.13)
- Modern web browser with Web Speech API support (Chrome, Edge, Firefox, Safari)

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt

# Copy .env.example to .env, then set JWT_SECRET_KEY to a random value from:
python -c "import secrets; print(secrets.token_urlsafe(48))"
# For disposable local demo data only, set SEED_DEMO_DATA=true and
# AUTO_CREATE_SCHEMA=true in backend/.env. Production must keep both false.
uvicorn app.main:app --reload --port 8000
```
Backend API will run at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend
npm install
# Copy .env.example to .env.local for local API access
npm run dev
```
Frontend will run at `http://localhost:5173`.

---

## 👥 Demo Accounts

When `ENVIRONMENT=development`, `SEED_DEMO_DATA=true`, and `AUTO_CREATE_SCHEMA=true`, the local database is seeded with demo accounts. These accounts are not created in production.

| Role | Email | Password | Description |
| :--- | :--- | :--- | :--- |
| **Teacher** | `teacher@ableconnect.org` | `teacher123` | Sarah Jenkins - Inclusive Ed Lead |
| **Student (Visual/AAC)** | `leo@ableconnect.org` | `student123` | Leo Vance - Prefers AAC picture cards & TTS |
| **Student (Sensory)** | `maya@ableconnect.org` | `student123` | Maya Patel - Prefers clear step-by-step instructions |
| **Student (Help/Direct)** | `sam@ableconnect.org` | `student123` | Sam Rivera - Prefers audio prompts & prompt help |
| **Guardian** | `guardian@ableconnect.org` | `guardian123` | David Chen - Authorized parent of Leo |

---

## ♿ Accessibility Compliance (WCAG 2.2 AA)

- **Contrast:** Meets and exceeds 4.5:1 ratio for normal text and 3:1 for large interactive elements. Dedicated High Contrast theme available.
- **Font Scaling:** Dynamic text size adjustment (Default, Large, Extra Large) with relative rem units.
- **Motion Reduction:** Respects `prefers-reduced-motion` and includes an on-screen toggle to eliminate transitions for vestibular safety.
- **Non-Speech / Non-Mouse Alternatives:** Full keyboard tab navigation, visual AAC sentence builder with single-touch selection, and audio synthesis feedback.
