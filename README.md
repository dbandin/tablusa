# Tabnote

Tabnote is an in-progress terminal editor for durable personal guitar and bass
tabs. The native v1 format and fixtures are documented in `SPEC.md` and
`docs/format.md`.

The document core and minimum terminal editor are available. Practical notation
menus, metadata editing and HTML export are still planned increments.

## Dev env and usage

Planned development environment:

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
```

Run an existing tab, or create a blank bass tab (use `--instrument guitar` for
guitar):

```bash
tabnote --instrument (guitar|bass) song.tab
```
## Screenshots

Normal, insert and command modes.

<img width="852" height="700" alt="image" src="https://github.com/user-attachments/assets/827763b5-f411-4567-a4dd-71e57da97df4" />

<img width="851" height="699" alt="image" src="https://github.com/user-attachments/assets/849d0ffd-50eb-4b38-8545-cd85e89ef63e" />
