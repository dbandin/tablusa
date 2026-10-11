"""Minimum modal Textual editor backed by the pure document core."""

from __future__ import annotations

import re
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.events import Key
from textual.widgets import Input, Static

from ..editing import EditError, History, clear_token, delete_room, insert_room, set_token
from ..format import mark_saved, new_document, parse
from ..storage import ExternalModificationError, FileStamp, save, stamp

_TOKEN_RUN = re.compile(r"[^-|]+")


class TabnoteApp(App[None]):
    """A deliberately small modal editor for one recognized document group."""

    CSS = """
    Screen { layout: vertical; }
    #grid { height: 1fr; border: round $accent; }
    #notation { width: auto; min-width: 164; }
    #status { height: 1; background: $panel; padding: 0 1; }
    #command { display: none; }
    """

    def __init__(self, path: Path, instrument: str = "bass") -> None:
        super().__init__()
        self.path = path
        self.mode = "NORMAL"
        self.buffer = ""
        self.group_index = 0
        self.string_index = 0
        self.column = 0
        if path.exists():
            self.history = History(parse(path.read_text(encoding="utf-8")))
            self.file_stamp: FileStamp | None = stamp(path)
        else:
            self.history = History(new_document(instrument))
            self.file_stamp = None

    def compose(self) -> ComposeResult:
        yield ScrollableContainer(Static(id="notation"), id="grid")
        yield Input(placeholder="Command", id="command")
        yield Static(id="status")

    def on_mount(self) -> None:
        self.refresh_view()

    @property
    def document(self):
        return self.history.current

    def refresh_view(self, message: str = "") -> None:
        lines: list[str] = []
        for group_number, group in enumerate(self.document.groups):
            lines.append(f"[group {group_number + 1}{'' if group.editable else ': read-only'}]")
            for string_number, (label, row) in enumerate(zip(group.labels, group.rows)):
                marker = ">" if (group_number, string_number) == (self.group_index, self.string_index) else " "
                lines.append(f"{marker}{label}|{row}")
        self.query_one("#notation", Static).update("\n".join(lines))
        dirty = "*" if self.document.dirty else ""
        buffer = f" buffer={self.buffer!r}" if self.mode == "EDIT" else ""
        self.query_one("#status", Static).update(
            f"{self.mode}{dirty}  group={self.group_index + 1} string={self.string_index + 1} column={self.column + 1}{buffer}  {message}"
        )

    def on_key(self, event: Key) -> None:
        if self.mode == "COMMAND":
            return
        if self.mode == "EDIT":
            self._handle_edit_key(event)
            return
        if self.mode == "READ":
            if event.key == "escape":
                self.mode = "NORMAL"
                self.refresh_view()
            return
        self._handle_normal_key(event)

    def _handle_normal_key(self, event: Key) -> None:
        key = event.key
        if key in {"h", "left"}:
            self._move_horizontal(-1)
        elif key in {"l", "right"}:
            self._move_horizontal(1)
        elif key in {"j", "down"}:
            self.string_index = min(self.string_index + 1, len(self._group().rows) - 1)
        elif key in {"k", "up"}:
            self.string_index = max(self.string_index - 1, 0)
        elif key in {"i", "enter"}:
            self.mode, self.buffer = "EDIT", ""
        elif key == "x":
            token = self._token_at_cursor()
            if token:
                self._commit(clear_token(self.document, self.group_index, self.string_index, self.column, len(token)))
        elif key == "o":
            self._try(lambda: insert_room(self.document, self.group_index, min(self.column + 1, 160)))
        elif key == "d":
            self._try(lambda: delete_room(self.document, self.group_index, self.column))
        elif key == "u":
            self.history = self.history.undo()
        elif key == "ctrl+r":
            self.history = self.history.redo()
        elif key in {":", "colon"}:
            self.mode = "COMMAND"
            command = self.query_one("#command", Input)
            command.styles.display = "block"
            command.value = ":"
            command.focus()
        elif key in {"?", "question_mark"}:
            self.refresh_view("i edit; Enter/move commits; :w save; :q quit")
            return
        self.refresh_view()

    def _handle_edit_key(self, event: Key) -> None:
        if event.key == "escape":
            self.mode, self.buffer = "NORMAL", ""
        elif event.key == "enter":
            self._finish_edit(1)
        elif event.key in {"h", "left", "l", "right", "j", "up", "k", "down"}:
            direction = -1 if event.key in {"h", "left"} else 1
            if self._finish_edit(direction):
                if event.key in {"j", "down"}:
                    self.string_index = min(self.string_index + 1, len(self._group().rows) - 1)
                elif event.key in {"k", "up"}:
                    self.string_index = max(self.string_index - 1, 0)
        elif event.character and event.character.isascii() and event.character.isprintable():
            self.buffer += event.character
        self.refresh_view()

    def _finish_edit(self, direction: int) -> bool:
        if not self.buffer:
            self.mode = "NORMAL"
            return True
        token = self._token_at_cursor()
        try:
            document = self.document
            if token:
                document = clear_token(document, self.group_index, self.string_index, self.column, len(token))
            document = set_token(document, self.group_index, self.string_index, self.column, self.buffer)
        except EditError as error:
            self.refresh_view(str(error))
            return False
        self.history = self.history.commit(document)
        self.mode, self.buffer = "NORMAL", ""
        self._move_horizontal(direction)
        return True

    def _group(self):
        return self.document.groups[self.group_index]

    def _anchors(self) -> list[int]:
        anchors = {0}
        for row in self._group().rows:
            anchors.update(match.start() for match in _TOKEN_RUN.finditer(row))
        return sorted(anchors)

    def _move_horizontal(self, direction: int) -> None:
        anchors = self._anchors()
        if direction < 0:
            choices = [anchor for anchor in anchors if anchor < self.column]
            self.column = choices[-1] if choices else 0
        else:
            choices = [anchor for anchor in anchors if anchor > self.column]
            self.column = choices[0] if choices else min(self.column + 1, 159)

    def _token_at_cursor(self) -> str | None:
        row = self._group().rows[self.string_index]
        for match in _TOKEN_RUN.finditer(row):
            if match.start() <= self.column < match.end():
                self.column = match.start()
                return match.group(0)
        return None

    def _commit(self, document) -> None:
        self.history = self.history.commit(document)

    def _try(self, operation) -> None:
        try:
            self._commit(operation())
        except EditError as error:
            self.refresh_view(str(error))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        command = event.value.strip()
        field = self.query_one("#command", Input)
        field.styles.display = "none"
        self.mode = "NORMAL"
        self.set_focus(None)
        self._run_command(command)

    def _run_command(self, command: str) -> None:
        parts = command.lstrip(":").split(maxsplit=1)
        name = parts[0] if parts else ""
        argument = parts[1] if len(parts) == 2 else None
        if name in {"w", "wq"}:
            target = Path(argument) if argument else self.path
            try:
                self.file_stamp = save(self.document, target, self.file_stamp if target == self.path else None)
                self.path = target
                self.history = History(mark_saved(self.document), self.history.undo_stack, self.history.redo_stack)
                if name == "wq":
                    self.exit()
                self.refresh_view("saved")
            except (OSError, ExternalModificationError) as error:
                self.refresh_view(f"save failed: {error}")
        elif name == "q":
            self.refresh_view("unsaved changes: use :q!" if self.document.dirty else "quitting")
            if not self.document.dirty:
                self.exit()
        elif name == "q!":
            self.exit()
        elif name == "view":
            self.mode = "READ"
            self.refresh_view("Escape returns to Normal")
        elif name == "help":
            self.refresh_view("Normal: i x o d u Ctrl-R : ?; Edit: type token, Enter commits")
        else:
            self.refresh_view(f"unknown command: {command}")
