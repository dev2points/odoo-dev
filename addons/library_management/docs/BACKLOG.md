# Library Management Backlog

## Completed Direction

- Manifest now points to the active XML and data files.
- Dashboard client action is wired.
- Borrow/member/copy/shelf views are aligned with the current models.
- Borrow and dashboard helper methods exist in backend Python.

## Remaining Gaps

- `library_book_views.xml` is still in the repository as legacy UI and can confuse future work.
- `library.fine` exists but is not yet part of the active borrow/return workflow.
- There is no formal test suite or QA checklist for borrow/return scenarios yet.
- Some model names in the historical README still refer to `library.book.copy`; the code currently uses `stock.lot` for physical copies.

## Recommended Next Tasks

1. Remove or archive legacy XML that is not loaded.
2. Add a minimal manual QA checklist for create-confirm-borrow-return-cancel flows.
3. Decide whether to introduce a dedicated copy model or keep using `stock.lot`.
4. Wire fines into overdue/lost/damaged handling.
5. Add migration notes for future agents if the model choice changes.
