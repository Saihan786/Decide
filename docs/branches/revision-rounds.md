# feature/revision-rounds

## Goal
Allow the writer to revise the document and send it out for another round of review.

## Scope
- From the results page, writer can choose to start a new revision round
- A new `Document` is created with an incremented revision number, pre-loaded with the previous content
- Session resets to the writing phase — existing reviewers are retained
- Previous rounds (documents + reviews) remain stored and accessible

## Outcome
The session supports multiple revision cycles. Each round's document and reviews are preserved for reference.
