from __future__ import annotations

import asyncio
from pathlib import Path

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
