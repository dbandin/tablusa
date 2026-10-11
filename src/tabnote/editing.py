"""Pure document edits and reversible history."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .model import Document, GRID_WIDTH, StringGroup

_VALID_TOKEN = re.compile(r"(?:[0-9]|[12][0-9]|3[0-6]|x)(?:(?:h|p|/|\\)(?:[0-9]|[12][0-9]|3[0-6])|~|=|b(?:[0-9]|[12][0-9]|3[0-6])(?:r(?:[0-9]|[12][0-9]|3[0-6]))?)?$")


class EditError(ValueError):
    pass


def set_token(document: Document, group_index: int, string_index: int, column: int, token: str) -> Document:
    if not _VALID_TOKEN.fullmatch(token):
        raise EditError(f"unsupported token: {token!r}")
    group = document.groups[group_index]
    if not group.editable:
        raise EditError("group is read-only due to format diagnostics")
    if not 0 <= string_index < len(group.rows) or not 0 <= column < GRID_WIDTH:
        raise EditError("string or column is outside the group")
    if column + len(token) > GRID_WIDTH:
        raise EditError("token would exceed column 160")
    row = group.rows[string_index]
    if any(char != "-" for char in row[column : column + len(token)]):
        raise EditError("target must be empty; clear or make room first")
    if column and row[column - 1] not in "-|":
        raise EditError("a token needs a separating hyphen")
    if column + len(token) < GRID_WIDTH and row[column + len(token)] not in "-|":
        raise EditError("a token needs a separating hyphen")
    rows = list(group.rows)
    rows[string_index] = row[:column] + token + row[column + len(token) :]
    return document.replace_group(group_index, StringGroup(group.line_start, group.labels, tuple(rows)))


def clear_token(document: Document, group_index: int, string_index: int, column: int, width: int) -> Document:
    group = document.groups[group_index]
    if not group.editable:
        raise EditError("group is read-only due to format diagnostics")
    if width < 1 or not 0 <= column <= GRID_WIDTH - width:
        raise EditError("clear range is outside the group")
    rows = list(group.rows)
    row = rows[string_index]
    rows[string_index] = row[:column] + "-" * width + row[column + width :]
    return document.replace_group(group_index, StringGroup(group.line_start, group.labels, tuple(rows)))


def insert_room(document: Document, group_index: int, column: int, width: int = 1) -> Document:
    if width < 1 or not 0 <= column <= GRID_WIDTH:
        raise EditError("insert range is outside the group")
    group = document.groups[group_index]
    if not group.editable:
        raise EditError("group is read-only due to format diagnostics")
    if any(any(char != "-" for char in row[-width:]) for row in group.rows):
        raise EditError("not enough trailing room in 160-column group")
    rows = tuple(row[:column] + "-" * width + row[column : GRID_WIDTH - width] for row in group.rows)
    return document.replace_group(group_index, StringGroup(group.line_start, group.labels, rows))


def delete_room(document: Document, group_index: int, column: int, width: int = 1) -> Document:
    group = document.groups[group_index]
    if width < 1 or not 0 <= column <= GRID_WIDTH - width:
        raise EditError("delete range is outside the group")
    if any(any(char != "-" for char in row[column : column + width]) for row in group.rows):
        raise EditError("can only delete empty aligned room")
    rows = tuple(row[:column] + row[column + width :] + "-" * width for row in group.rows)
    return document.replace_group(group_index, StringGroup(group.line_start, group.labels, rows))


@dataclass(frozen=True)
class History:
    current: Document
    undo_stack: tuple[Document, ...] = ()
    redo_stack: tuple[Document, ...] = ()

    def commit(self, document: Document) -> "History":
        return History(document, self.undo_stack + (self.current,), ())

    def undo(self) -> "History":
        if not self.undo_stack:
            return self
        return History(self.undo_stack[-1], self.undo_stack[:-1], self.redo_stack + (self.current,))

    def redo(self) -> "History":
        if not self.redo_stack:
            return self
        return History(self.redo_stack[-1], self.undo_stack + (self.current,), self.redo_stack[:-1])
