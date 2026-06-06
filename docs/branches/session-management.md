# feature/session-management

## Goal
Allow a writer to create a session and reviewers to join it by code.

## Scope
- ☑ `Session`, `Writer`, and `Reviewer` models
- ☑ Writer lands on home page and creates a session — generates a unique join code
- ☑ Writer sees the join code and a waiting screen showing who has joined so far
- ☑ Reviewer navigates to `/join/<code>`, enters their name, and joins the session
- ☐ Session enforces a maximum of 10 reviewers

## Outcome
A session exists in the database with a writer and up to 10 named reviewers attached to it. The writer can see who has joined and move to the writing phase when ready.
