# Decide — Project Scope

## Overview
Decide is a solo-built web application that facilitates a structured document review process. A writer drafts a document and submits it to a group of reviewers, who each independently approve or disapprove with comments. The writer receives a consolidated result.

---

## Users
- Up to 10 users per session
- No authentication — users identify by entering their name
- Two roles:
  - **Writer** — creates the session and authors the document
  - **Reviewers** — join via a session code/link and review the submitted document

---

## Core Flow

### 1. Session Creation
- Writer starts a new session and receives a shareable code or link (Kahoot-style)
- Reviewers navigate to the app, enter the code/link, and enter their name to join

### 2. Writing Phase
- Writer sees a rich text editor (Word-like interface)
- Writer can save progress and return over multiple days
- Reviewers see a waiting screen until the document is submitted

### 3. Review Phase
- Triggered when the writer submits the document
- Each reviewer independently:
  - Reads through the document
  - Submits inline or general comments
  - Approves or disapproves with a written reason
- Reviewers cannot see each other's responses until all have submitted

### 4. Result Phase
- Once all reviewers have submitted, the writer sees:
  - Overall approval/disapproval outcome
  - All individual comments and reasons

---

## Stretch Goals (in scope if time allows)
- **Revision rounds** — after receiving feedback, writer can revise and resubmit for another review cycle
- Rich text editing (if integration proves complex, plain text is acceptable as a fallback)

---

## Out of Scope
- User authentication / accounts / login
- Notifications (email, SMS, push)
- Multiple documents per session
- Reviewer-to-reviewer visibility during review phase

---

## Tech Stack
- **Backend:** Python / Django
- **Frontend:** Django templates + HTMX (for lightweight interactivity without a full JS framework)
- **Rich text editor:** Quill.js or TipTap
- **Database:** Relational DB (SQLite for development, PostgreSQL for production)
- **Real-time updates:** Page refresh (WebSockets/Django Channels not required for v1)

---

## Data Storage
The following must be persisted:
- Session metadata (code, status, participants)
- Document content (per session, per revision round)
- Reviewer responses (comments, approval/disapproval, reason)

---

## Timeline
TBD — solo project, no fixed deadline. Suggested phasing:

| Phase | Scope |
|-------|-------|
| 1 | Session creation, joining, writer editor, document submission |
| 2 | Review flow, comments, approve/disapprove, result display |
| 3 | Stretch goals (revision rounds, rich text polish) |
