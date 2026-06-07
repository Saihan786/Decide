# feature/review-flow

## Goal
Allow each reviewer to independently read the document and submit their response.

## Scope
- ☑ `Review` model (linked to reviewer and document — stores approval decision, reason, and comments)
- ☐ Reviewer sees the document rendered as read-only
- ☐ Reviewer submits: approve or disapprove with a written reason, plus any comments
- ☐ Reviewers cannot see each other's responses
- ☐ Once all reviewers have submitted, session transitions to the result phase
- ☐ Writer sees a waiting screen (HTMX polling) until all reviews are in

## Outcome
All reviewer responses are saved to the database and the session status moves to `result`.
