# Tabnote v0.1 keybindings

Normal mode navigates token anchors; Edit mode owns a pending ASCII token.
The grid keeps the active logical anchor visible with a high-contrast cursor.
Its ASCII ruler is 1-based: numbered ten-column marks, five-column ticks and
aligned internal barlines are visual navigation aids only.

| Key | Action |
| --- | --- |
| h/l or Left/Right | Previous/next token anchor |
| j/k or Down/Up | Same anchor on adjacent string |
| i, Enter | Edit selected anchor |
| x | Clear token |
| o/d | Insert/delete one aligned empty position |
| t | Technique menu |
| u, Ctrl-R | Undo/redo |
| : / ? | Commands/help |

Edit mode takes a complete literal token. Enter commits/advances, movement commits
and moves, Escape discards. Digits never timeout. Commands are :w, :w path, :q,
:q!, :wq, :help, :view and :export html path; none invoke a shell.
