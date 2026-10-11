from __future__ import annotations

from pathlib import Path

import pytest

from tabnote.editing import History, clear_token, insert_room, set_token
from tabnote.format import parse, serialize
from tabnote.storage import ExternalModificationError, save, stamp


FIXTURES = Path(__file__).parent / "fixtures"


def test_fixture_round_trip_is_byte_identical() -> None:
    source = (FIXTURES / "bass_demo.tab").read_text()
    document = parse(source)
    assert not document.diagnostics
    assert serialize(document) == source


def test_known_techniques_and_chord_alignment() -> None:
    document = parse((FIXTURES / "guitar_demo.tab").read_text())
    group = document.groups[0]
    assert group.editable
    assert group.rows[0].index("12") == group.rows[1].index("12")
    assert "5h7" in group.rows[1]
    assert "7/9" in group.rows[2]
    assert "7b9r7" in group.rows[3]
    assert "7=" in group.rows[4]


def test_insert_clear_undo_redo_across_whole_group() -> None:
    original = parse((FIXTURES / "bass_demo.tab").read_text())
    inserted = insert_room(original, 0, 100, 2)
    assert all(row[100:102] == "--" for row in inserted.groups[0].rows)
    changed = set_token(inserted, 0, 0, 100, "12")
    cleared = clear_token(changed, 0, 0, 100, 2)
    history = History(original).commit(inserted).commit(changed).commit(cleared)
    after_undo = history.undo()
    assert after_undo.current == changed
    assert after_undo.undo().current == inserted
    assert after_undo.redo().current == cleared


def test_malformed_group_is_read_only_and_source_is_preserved() -> None:
    source = "# tabnote: 1\nInstrument: bass\nG|---\n"
    document = parse(source)
    assert document.diagnostics
    assert not document.groups[0].editable
    assert serialize(document) == source


def test_unknown_token_is_preserved_with_a_diagnostic() -> None:
    source = (FIXTURES / "bass_demo.tab").read_text().replace("7~", "7z")
    document = parse(source)
    assert any("unrecognized token" in item.message for item in document.diagnostics)
    assert serialize(document) == source


def test_atomic_save_preserves_permissions_and_detects_external_change(tmp_path: Path) -> None:
    path = tmp_path / "song.tab"
    path.write_text((FIXTURES / "bass_demo.tab").read_text())
    path.chmod(0o640)
    document = parse(path.read_text())
    baseline = stamp(path)
    result = save(document, path, baseline)
    assert result == stamp(path)
    assert path.stat().st_mode & 0o777 == 0o640
    path.write_text("external change\n")
    with pytest.raises(ExternalModificationError):
        save(document, path, result)


def test_headless_edit_save_and_reload(tmp_path: Path) -> None:
    source = (FIXTURES / "bass_demo.tab").read_text()
    edited = set_token(parse(source), 0, 0, 100, "12")
    path = tmp_path / "edited.tab"
    save(edited, path)
    reopened = parse(path.read_text())
    assert not reopened.diagnostics
    assert reopened.groups[0].rows[0][100:102] == "12"
