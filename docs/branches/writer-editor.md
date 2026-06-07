# feature/writer-editor

## Goal
Give the writer a rich text editor to compose and save their document.

## Scope
- ☑ `Document` model (linked to session, stores content and revision number)
- ☑ Writer sees a Quill.js editor pre-loaded with any previously saved content
- ☑ Writer can save progress and return later — session persists across sittings
- ☐ Writer submits the document when ready, transitioning the session to the review phase
- ☑ Reviewers see a waiting screen until the document is submitted

## Outcome
A document is saved to the database and the session status moves to `review`. Reviewers are unblocked.
