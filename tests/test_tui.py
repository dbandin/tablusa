from __future__ import annotations

import asyncio
from pathlib import Path

from tabnote.model import StringGroup
from tabnote.tui.app import TabnoteApp


def test_modal_edit_save_and_read_mode(tmp_path: Path) -> None:
    path = tmp_path / "new.tab"

    async def exercise() -> None:
        app = TabnoteApp(path, "bass")
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.press("i", "1", "2", "enter")
            assert app.document.dirty
            assert app.document.groups[0].rows[0].startswith("12")
            await pilot.resize_terminal(50, 12)
            assert app.column == 1
            await pilot.press("colon", "w", "enter")
            assert path.exists()
            assert not app.document.dirty
            await pilot.press("colon", "v", "i", "e", "w", "enter")
            assert app.mode == "READ"
            await pilot.press("escape")
            assert app.mode == "NORMAL"

    asyncio.run(exercise())


def test_grid_ruler_cursor_styles_and_viewport_follow(tmp_path: Path) -> None:
    path = tmp_path / "grid.tab"

    async def exercise() -> None:
        app = TabnoteApp(path, "bass")
        async with app.run_test(size=(30, 12)) as pilot:
            group = app.document.groups[0]
            rows = tuple(row[:20] + "|" + row[21:] for row in group.rows)
            app.history = app.history.commit(
                app.document.replace_group(
                    0, StringGroup(group.line_start, group.labels, rows)
                )
            )
            app.refresh_view()

            rendered = app.query_one("#notation").renderable
            assert "1         11        21" in rendered.plain
            ruler = rendered.plain.splitlines()[2]
            assert ruler[23] == "|"
            assert any(span.style == "bold reverse" for span in rendered.spans)
            assert any(span.style == "on $boost" for span in rendered.spans)

            for _ in range(12):
                await pilot.press("right")
            assert app.column == 12
            assert app.query_one("#grid").scroll_x > 0

            await pilot.press("down")
            rendered = app.query_one("#notation").renderable
            assert "\n>D|" in rendered.plain
            assert any(span.style == "bold reverse" for span in rendered.spans)

            await pilot.resize_terminal(80, 6)
            assert app.column == 12

    asyncio.run(exercise())
