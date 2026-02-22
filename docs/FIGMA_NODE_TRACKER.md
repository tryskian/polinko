# Figma Node Tracker

Use this as the implementation order so nodes are finished end-to-end without jumping.

## Workflow

1. Select node in Figma and share link (`node-id=...`).
2. Extract context + screenshot + variables.
3. Implement in `frontend/` with project conventions.
4. Validate `cd frontend && npm run build`.
5. Mark node complete before moving to next.

## Progress

| Order | Node ID | Name | Status | Notes |
| --- | --- | --- | --- | --- |
| 1 | `2112:12011` | Color | Completed | Light/dark token foundation mapped into CSS variables. |
| 2 | `5:34018` | Desktop & Mobile Web / Controls | In progress | Theme dropdown implemented with Figma-style menu + state tokens + keyboard nav. |
| 3 | TBD | Next selected node | Pending | Send next node link after controls sign-off. |

## Current Focus: `5:34018`

- Header control patterns
- Dropdown menu states (default/hover/selected)
- Keyboard interaction parity for menu navigation
- Button state token mapping (default/hover/press)

