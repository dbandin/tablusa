# Tabnote v1 format

Files are UTF-8 and begin exactly with # tabnote: 1. Top-level metadata precedes
the first [section]. Recognized metadata is Title, Artist, Instrument, Tuning,
Meter, Tempo, Repeat, Note and Source. Note/Source repeat. Unknown metadata,
comments, blanks and raw blocks remain verbatim.

Instrument is guitar (six rows, E4 B3 G3 D3 A2 E2) or bass (four rows,
G2 D2 A1 E1). Each complete group has that many consecutive rows:

    <label>|<160 notation characters>

The first bar is outside the notation area. Padding is hyphen. Groups repeat
after blank lines. Tokens occupy consecutive columns; chords share starts; token
neighbours need a hyphen. Internal bars align across every group row and are
visual only. Recognize frets 0–36, x, and generalized hammer, pull, slide,
vibrato, bend/release and tie tokens. Unknown text is retained/diagnosed.

Wider edits insert aligned room across the active group and fail past column 160.
Untouched files write byte-identically. Only changed recognized groups may
canonicalize. Bad row counts, inconsistent bars and wrong widths are read-only
diagnostics. Unsupported versions and old separator drafts remain raw.

