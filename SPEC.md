# Tabnote — product specification

Status: proposed v0.1.

## Purpose

Tabnote is a small terminal application for a durable personal guitar/bass
songbook. Fast entry, reliable alignment and readable independent files matter
more than music engraving. Use Python 3.11+ and Textual; keep parser, model,
storage and HTML export independent of the TUI. No services, accounts, network,
playback, transcription, standard notation or cloud features.

Core v0.1 supports guitar/bass, frets 0–36, x, chords, techniques, sections,
notes/sources, meter/tempo/repeats, safe persistence, reading and HTML. Rhythm
durations, extra string counts and richer selection are deferred.

## Interaction

Use a custom grid and show mode, section, string, token anchor and dirty state.
h/l or arrows move token anchors; j/k preserve the horizontal anchor. i or Enter
edits; Enter or directional movement commits; Escape drops only pending input.
x clears, o inserts and d deletes one aligned empty character position. t opens
techniques, u/Ctrl-R undo/redo, : opens application commands, and ? opens help.
Digits never timeout: 12 is one token. Technique tokens are typed literally.

## Native format

Files are UTF-8 and begin with # tabnote: 1. Native v1 is continuous-hyphen
notation, replacing the unreleased separator draft. A section contains one or
more complete string groups. Each row is:

    <label>|<exactly 160 ASCII notation characters>

The first bar separates the label and is outside the notation area. Long sections
repeat a complete labelled four-string bass or six-string guitar group after a
blank line. Bass tuning is G2 D2 A1 E1; guitar is E4 B3 G3 D3 A2 E2.

Tokens begin at logical ASCII columns, occupy consecutive columns, and have at
least one hyphen before a following token. Chords share a start column. Internal
bars are optional aligned visual barlines only: they do not define cells or
duration. A long token shifts later content across every row in its group; reject
an edit past column 160. Meter/tempo/barlines/repeats are annotations only;
timing changes start a new named section.

Recognize 0–36, x, hammers, pulls, slides, vibrato, bend/release and ties such
as 5h7, 7p5, 5/7, 7-backslash-5, 7~, 7b9, 7b9r7, 7=. Note: and Source: repeat in
document/section headers. Unknown tokens and text are retained and diagnosed.

## Preservation and output

Unedited input round-trips byte-for-byte. Changed recognized groups may
canonicalize; unknown metadata/comments/raw blocks remain verbatim. Malformed
groups are read-only with line diagnostics. Unsupported versions and old
separator-shaped drafts are raw/read-only, never converted silently.

Plain mode is complete. Optional patched-font symbols are UI chrome only, never
grid/saved notation. Save atomically, preserve permissions, detect external
changes, retain dirty state on error and escape HTML. Print only whole groups.
