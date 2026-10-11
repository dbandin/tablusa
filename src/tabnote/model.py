"""Typed, terminal-independent Tabnote document types."""

from __future__ import annotations

from dataclasses import dataclass, replace


GRID_WIDTH = 160


@dataclass(frozen=True)
class Diagnostic:
    line: int
    message: str


@dataclass(frozen=True)
class StringGroup:
    line_start: int
    labels: tuple[str, ...]
    rows: tuple[str, ...]
    editable: bool = True


@dataclass(frozen=True)
class Document:
    source: str
    lines: tuple[str, ...]
    groups: tuple[StringGroup, ...]
    diagnostics: tuple[Diagnostic, ...] = ()
    changed_groups: frozenset[int] = frozenset()

    @property
    def dirty(self) -> bool:
        return bool(self.changed_groups)

    def replace_group(self, index: int, group: StringGroup) -> "Document":
        groups = list(self.groups)
        groups[index] = group
        return replace(self, groups=tuple(groups), changed_groups=self.changed_groups | {index})
