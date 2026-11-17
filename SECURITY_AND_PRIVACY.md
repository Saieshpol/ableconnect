# AbleConnect: Security, Child Safety & Privacy Architecture

This document governs the privacy, security, and child data protection standards enforced across the AbleConnect platform.

> **Deployment status:** This repository has security controls and deployment preparation, but has not passed a full production privacy/security review. Do not enter real student or disability data until the release checklist in `DEPLOYMENT.md` is completed. Login throttling, password reset/invitations, malware scanning, backup restoration tests, and independent security review remain outstanding.

---

## 1. Ethical Stance on Disability & Student Data

1. **No Automated Diagnostic Labeling:**
   AbleConnect **never** infers or assigns disability diagnoses, psychological conditions, or medical classifications based on student requests, emotion check-ins, or communication frequencies.
2. **Support Over Labeling:**
   The platform focuses strictly on *functional communication preferences* (e.g. "prefers pictures", "needs processing time") rather than displaying clinical diagnostics.
3. **No External AI Training on Student Communication:**
   Student messages, picture sequences, help requests, and private teacher observations are **never** shared with third parties or used to train public machine learning models.
4. **Teacher and Guardian Authority:**
   All communication guidelines and support strategies must be explicitly entered or approved by authorized human educators or guardians.

---

## 2. Role-Based Access Control (RBAC) Matrix

| Resource | Teacher | Student | Guardian | Admin |
| :--- | :---: | :---: | :---: | :---: |
| **All Class Rosters** | Assigned Classes Only | None | None | All |
| **Student Public Profile Card** | Basic (Name, Avatar, Class) | Own Profile | Linked Child Only | All |
| **Student Support & Sensory Profile** | Assigned Students Only | Own Profile | Linked Child Only | All |
| **Student Communication Boards** | Read/Edit for Class | View/Use Own | View Linked Child | Manage |
| **Help Requests** | View/Respond for Class | Create/View Own | View for Linked Child | All |
| **Emotion Check-ins** | View (Aggregated/Class) | Submit/Skip Own | View for Linked Child | None |
| **Confidential Teacher Observations**| Read/Write (Author/Assigned) | ❌ Restricted | ❌ Restricted | Audit Only |
| **Two-Way Messages** | Class Students & Guardians | Assigned Teachers Only | Assigned Teachers Only | Audit Only |

---

## 3. Data Protection Safeguards

- **Password Security:** Passwords hashed with bcrypt using high work-factor salts.
- **Session Tokens:** Stateless JWT tokens signed with HMAC-SHA256, verified on every protected route.
- **Zero Public Search Indexing:** Student profiles are strictly unindexed (`noindex, nofollow`) and behind authentication barriers.
- **Audit Trails:** Edits to sensitive support instructions or guardian permissions generate timestamped audit records.
- **Data Minimization:** Only data required for classroom communication and safety is stored. Medical diagnosis numbers (ICD/DSM codes) are never recorded.
