# Tabnote

Tabnote is an in-progress terminal editor for durable personal guitar and bass
tabs. The native v1 format and fixtures are documented in `SPEC.md` and
`docs/format.md`.

The document core and minimum terminal editor are available. Practical notation
menus, metadata editing and HTML export are still planned increments.

Planned development environment:

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
```

Run an existing tab, or create a blank bass tab (use `--instrument guitar` for
guitar):

```bash
tabnote song.tab
```
