# AbleConnect: REST API Documentation

The AbleConnect API is built using **FastAPI** with automatic OpenAPI (Swagger) documentation generated at `/docs` and ReDoc at `/redoc`.

Base URL: `http://localhost:8000/api`

---

## 🔐 Authentication & Session Endpoints

### 1. `POST /api/auth/login`
Authenticates a user and returns a signed JWT Bearer token with user details and assigned role.
- **Request Body**:
  ```json
  {
    "email": "teacher@ableconnect.org",
    "password": "teacher123"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "teacher@ableconnect.org",
      "full_name": "Sarah Jenkins",
      "role": "teacher",
      "avatar_url": null
    }
  }
  ```

### 2. `GET /api/auth/me`
Fetches the authenticated user profile based on the JWT `Authorization: Bearer <token>` header.

### 3. `POST /api/auth/demo-switch`
Switches authentication context instantly between demo roles (`teacher`, `student`, `guardian`) for evaluation, testing, and paired communication trials.

---

## 🏫 Classes & Students Endpoints

### 1. `GET /api/classes`
Lists all classes managed by the authenticated teacher, or classes enrolled for a student.
- **Query Params**: `include_students=true`
- **Response**: Array of class objects with student counts and schedules.

### 2. `POST /api/classes`
Creates a new classroom.
- **Payload**:
  ```json
  {
    "name": "Inclusive Room 102 - Grade 3",
    "grade_level": "Grade 3",
    "room": "Room 102",
    "color_theme": "teal"
  }
  ```

### 3. `GET /api/students`
Lists students accessible to the authenticated user.
- Teachers only see students enrolled in their classes.
- Guardians only see authorized dependent students.
- Returns student summaries with preferred communication mode and essential teacher instructions.

### 4. `GET /api/students/{student_id}`
Returns the comprehensive profile of an individual student:
- Basic info
- Sensory profile & assistance level
- Communication preferences (AAC, TTS, speech rate)
- Teacher support instructions ("How to communicate with this student")
- Recent emotion check-in
- Recent observations (if authenticated as teacher)

### 5. `PUT /api/students/{student_id}/preferences`
Updates a student's communication and sensory preferences.
- Allowed for teachers and authorized guardians.

---

## 🗣️ Communication & AAC Endpoints

### 1. `GET /api/communication/boards`
Fetches communication boards available to the student or teacher.
- Returns cards grouped by categories: `needs`, `emotions`, `classroom`, `actions`.

### 2. `POST /api/communication/synthesize-sentence`
Constructs a coherent, grammatical sentence from an array of selected symbol cards.
- **Payload**:
  ```json
  {
    "symbols": ["I", "Need", "Break"]
  }
  ```
- **Response**:
  ```json
  {
    "sentence": "I need a break.",
    "spoken_text": "I need a break.",
    "category": "needs"
  }
  ```

### 3. `POST /api/communication/requests`
Submits a non-stigmatizing student assistance request.
- **Payload**:
  ```json
  {
    "request_type": "break",
    "message": "I need a break."
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "id": 4,
    "student_id": 2,
    "request_type": "break",
    "status": "sent",
    "created_at": "2026-11-18T01:00:00Z"
  }
  ```

### 4. `GET /api/communication/requests`
Returns pending and historical help requests.
- Filter by status: `sent`, `seen`, `responded`, `resolved`.

### 5. `PATCH /api/communication/requests/{request_id}`
Updates a help request status (e.g. Teacher marks as `seen` or `responded` with an optional note).

### 6. `GET /api/communication/messages` & `POST /api/communication/messages`
Two-way direct messaging between teacher and student / guardian.

---

## 🛠️ Pedagogical Tools Endpoints

### 1. `POST /api/tools/simplify`
Simplifies standard instructions into step-by-step, plain-language items.
- **Payload**:
  ```json
  {
    "original_text": "Please open your science workbook to page 42, solve problems one through three, and put the book on the corner of your desk.",
    "reading_level": "simple",
    "add_visual_cues": true
  }
  ```
- **Response**:
  ```json
  {
    "original_text": "...",
    "steps": [
      {"step_number": 1, "text": "Open your science workbook to page 42.", "icon": "book-open"},
      {"step_number": 2, "text": "Solve problems 1, 2, and 3.", "icon": "edit-3"},
      {"step_number": 3, "text": "Put your book on the corner of your desk.", "icon": "check-circle"}
    ],
    "simplified_summary": "Open book to page 42, solve problems 1 to 3, place book on desk.",
    "audio_ready_text": "Step 1: Open your science workbook to page 42. Step 2: Solve problems 1, 2, and 3. Step 3: Put your book on the corner of your desk."
  }
  ```

### 2. `GET /api/tools/schedule`
Retrieves the visual timetable for a class or specific student.
