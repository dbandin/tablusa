# Tabnote — implementation plan

Status: active. Complete one increment before starting the next.

| Increment | Status | Completion record |
| --- | --- | --- |
| 0. Agree format and interactions | Complete | 2026-10-11 — Revised governing docs, added format/keybinding docs, pinned package metadata and original fixtures. Verified 160-column fixture areas and metadata parsing. No parser/TUI yet. |
| 1. Build document core | Complete | 2026-10-11 — Added terminal-independent parser/serializer, immutable edit/history operations, atomic storage and focused tests. Verified byte preservation, diagnostics, techniques, aligned room edits, undo/redo, edited save/reload, permissions and external-change protection. TUI remains unimplemented. |
| 2. Deliver minimum terminal editor | Complete | 2026-10-11 — Added the Textual modal grid, blank/open workflow, token entry, group room edits, save/quit commands, dirty protection, history, reading mode and resize-safe logical cursor. Verified Textual key sequence and resize harness checks plus a live terminal launch. Metadata editing and technique menu remain later work. |
| 2a. Polish music-forward grid navigation | Complete | 2026-10-11 — Added a styled, non-shifting logical-anchor cursor, active row/group hierarchy, 1-based ASCII column ruler with barline markers, compact feedback and resize-safe viewport follow. Verified with expanded Textual harness checks, `pytest` (9 passed), `ruff check .`, and a pseudo-terminal plain-mode launch. No parser, model, storage, format or keybinding changes. Next increment: practical notation and song structure. |
| 3. Add practical notation and song structure | Not started | — |
| 4. Export a practice sheet | Not started | — |
| 5. Package usable v0.1 | Not started | — |
| 6. Optional rhythm | Deferred | Begin after actual transcription sessions. |

On each completion record delivered behaviour, checks, limitations and next step.

## 0. Agree format and interactions — complete

Native v1 is fixed 160-column continuous-hyphen groups. Complete groups have
four bass or six guitar labelled rows; internal bars are aligned visuals only.
Tokens align in ASCII columns and wider edits shift later group content.
Patched-font decoration is optional UI chrome.

## 1. Build document core — complete

Parse sections/groups/token anchors, preserve opaque source, serialize changed
recognized groups only, implement set/clear and aligned room edits, history,
atomic save and external-change detection. Test byte/semantic round trips,
alignment, techniques, malformed preservation, undo/redo and failed saves.
Verified by the focused core test suite. The next increment is the minimum
terminal editor; no Textual UI behaviour has been implemented yet.

## 2. Deliver minimum terminal editor — complete

Add tabnote PATH, setup, custom grid/scrolling, modes, token/chord entry, room
operations, save/quit, dirty prompts, history and resize. The interactive
instrument choice is currently the `--instrument` command-line option.

Verified with the Textual test harness and a live 80-column terminal launch.
The next increment adds practical notation and song structure.

## 3–5

Add practical notation/metadata/reading/presentation; then escaped whole-group
HTML export; then install/run documentation, examples and platform smoke tests.

## 6. Optional rhythm

Design backward-compatible durations only after actual transcription sessions.
