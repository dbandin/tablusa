# Instructions for coding agents

Read SPEC.md and PLAN.md before changes. Implement exactly one active PLAN
increment at a time. When it completes, update PLAN.md with delivered behaviour,
verification, limitations and next increment; do not mark completion early.

Use Python/Textual, pinned dependencies and typed simple structures. Keep parser,
model, persistence and export independent of TUI. No services, accounts,
telemetry, AI, playback or network features.

The authoritative .tab file has 160 ASCII notation columns after a label bar.
Groups are four labelled bass or six labelled guitar rows, repeated whole for
long sections. Tokens occupy aligned columns, need a following hyphen before
another token and cannot cross an internal aligned visual bar. Preserve unknown
content; unedited files round-trip byte-for-byte. Changed recognized groups may
canonicalize under docs/format.md. Diagnose malformed content; atomic saves
preserve permissions/dirty state and detect external edits. Escape all HTML.

Use logical token anchors, not rendering offsets. Wider tokens shift later group
content across all rows as one undo action and cannot exceed 160 columns.
Plain mode is complete; patched-font glyphs are optional UI chrome only. Cover
preservation, techniques, chords, group edits/history, failures/conflicts, modal
keys/resizing, escaped HTML and whole print groups. Use original fixtures and
report unavailable manual checks honestly.
