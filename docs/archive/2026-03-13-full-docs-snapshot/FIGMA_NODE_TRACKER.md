# Figma Node Tracker

Use this as the implementation order so nodes are finished end-to-end without jumping.

## Workflow

1. Select node in Figma and share link (`node-id=...`).
2. Extract context + screenshot + variables.
3. Implement in `frontend/` with project conventions.
4. Validate `cd frontend && npm run build`.
5. Mark node complete before moving to next.

## Progress

| Order | Node ID | Name | Status | Notes | Link |
| --- | --- | --- | --- | --- | --- |
| 1 | `2112:12011` | Color | Completed | Light/dark token foundation mapped into CSS variables. | [Open](https://www.figma.com/design/PS3hM97jJX9hffihahgfzJ/Apps-in-ChatGPT-%E2%80%A2-Components---Templates--Community-?node-id=2112-12011&m=dev) |
| 2 | `5:34018` | Desktop & Mobile Web / Controls | Completed | Theme dropdown implemented with Figma-style menu + state tokens + keyboard nav in header controls. | [Open](https://www.figma.com/design/PS3hM97jJX9hffihahgfzJ/Apps-in-ChatGPT-%E2%80%A2-Components---Templates--Community-?node-id=5-34018&m=dev) |
| 3 | TBD | Next selected node | Pending | Send next node link after controls sign-off. | TBD |

## Current Focus: Await Next Node

- Controls pass on `5:34018` is completed.
- Next step: share the next node link and implement in order.
