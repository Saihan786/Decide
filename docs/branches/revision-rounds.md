Ah, I see what you mean! Standard Markdown relies on the platform (like GitHub, Notion, or your project management tool) to render those `[ ]` characters into interactive, clickable checkboxes.

If you are pasting this into a place that doesn't automatically convert Markdown syntax into UI elements, we can use literal Unicode checkbox characters (`☐` or `☑`) instead.

Here is the text updated with actual checkbox characters:

# feature/revision-rounds

## Goal

Allow the writer to revise the document and send it out for another round of review.

## Scope

- ☐ From the results page, writer can choose to start a new revision round
- ☐ A new `Document` is created with an incremented revision number, pre-loaded with the previous content
- ☐ Session resets to the writing phase — existing reviewers are retained
- ☐ Previous rounds (documents + reviews) remain stored and accessible

## Outcome

The session supports multiple revision cycles. Each round's document and reviews are preserved for reference.