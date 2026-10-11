"""Parser and serializer for the narrow Tabnote v1 dialect."""

from __future__ import annotations

import re
from dataclasses import replace

from .model import Diagnostic, Document, GRID_WIDTH, StringGroup

_ROW = re.compile(r"^([A-G](?:#|b)?)\|(.*)$")
_INSTRUMENT = re.compile(r"^Instrument:\s*(guitar|bass)\s*$", re.IGNORECASE)
_TOKEN = re.compile(r"(?:[0-9]|[12][0-9]|3[0-6]|x)(?:(?:h|p|/|\\)(?:[0-9]|[12][0-9]|3[0-6])|~|=(?=$|-|\|)|b(?:[0-9]|[12][0-9]|3[0-6])(?:r(?:[0-9]|[12][0-9]|3[0-6]))?)?")


def new_document(instrument: str) -> Document:
    """Create a valid blank v1 document for a supported instrument."""
    presets = {
        "bass": ("G2 D2 A1 E1", ("G", "D", "A", "E")),
        "guitar": ("E4 B3 G3 D3 A2 E2", ("E", "B", "G", "D", "A", "E")),
    }
    try:
        tuning, labels = presets[instrument]
    except KeyError as error:
        raise ValueError(f"unsupported instrument: {instrument}") from error
    source = "\n".join(
        ("# tabnote: 1", "Title: Untitled", f"Instrument: {instrument}", f"Tuning: {tuning}", "", "[Untitled]")
        + tuple(f"{label}|{'-' * GRID_WIDTH}" for label in labels)
        + ("",)
    )
    return parse(source)


def parse(text: str) -> Document:
    """Parse recognized groups while retaining every original line."""
    lines = tuple(text.splitlines(keepends=True))
    diagnostics: list[Diagnostic] = []
    if not lines or lines[0].rstrip("\r\n") != "# tabnote: 1":
        diagnostics.append(Diagnostic(1, "expected '# tabnote: 1' header"))

    instrument = next(
        (match.group(1).lower() for line in lines if (match := _INSTRUMENT.match(line.rstrip("\r\n")))),
        None,
    )
    expected_rows = {"guitar": 6, "bass": 4}.get(instrument)
    if expected_rows is None:
        diagnostics.append(Diagnostic(1, "missing or unsupported Instrument metadata"))

    groups: list[StringGroup] = []
    position = 0
    while position < len(lines):
        match = _ROW.match(lines[position].rstrip("\r\n"))
        if not match:
            position += 1
            continue
        start = position
        labels: list[str] = []
        rows: list[str] = []
        while position < len(lines) and (row := _ROW.match(lines[position].rstrip("\r\n"))):
            labels.append(row.group(1))
            rows.append(row.group(2))
            position += 1
        group_diagnostics = _validate_group(start, rows, expected_rows)
        diagnostics.extend(group_diagnostics)
        groups.append(StringGroup(start, tuple(labels), tuple(rows), not group_diagnostics))

    return Document(text, lines, tuple(groups), tuple(diagnostics))


def _validate_group(start: int, rows: list[str], expected_rows: int | None) -> list[Diagnostic]:
    errors: list[Diagnostic] = []
    if expected_rows is not None and len(rows) != expected_rows:
        errors.append(Diagnostic(start + 1, f"expected {expected_rows} string rows, found {len(rows)}"))
    widths = [len(row) for row in rows]
    for offset, width in enumerate(widths):
        if width != GRID_WIDTH:
            errors.append(Diagnostic(start + offset + 1, f"notation area is {width}, expected {GRID_WIDTH} columns"))
    if rows and len(set(widths)) == 1:
        bars = [{index for index, char in enumerate(row) if char == "|"} for row in rows]
        if len({tuple(sorted(bar_set)) for bar_set in bars}) != 1:
            errors.append(Diagnostic(start + 1, "internal barlines must align across every string"))
    for offset, row in enumerate(rows):
        for match in re.finditer(r"[^-|]+", row):
            if not _TOKEN.fullmatch(match.group(0)):
                errors.append(
                    Diagnostic(start + offset + 1, f"unrecognized token: {match.group(0)!r}")
                )
    return errors


def serialize(document: Document) -> str:
    """Return original bytes if untouched, otherwise replace changed groups only."""
    if not document.dirty:
        return document.source
    lines = list(document.lines)
    for index in sorted(document.changed_groups, reverse=True):
        group = document.groups[index]
        replacement = [f"{label}|{row}\n" for label, row in zip(group.labels, group.rows)]
        lines[group.line_start : group.line_start + len(group.rows)] = replacement
    return "".join(lines)


def mark_saved(document: Document) -> Document:
    """Return an equivalent clean document after a successful save."""
    source = serialize(document)
    return replace(document, source=source, lines=tuple(source.splitlines(keepends=True)), changed_groups=frozenset())
