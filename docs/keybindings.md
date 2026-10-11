# Tabnote v0.1 keybindings

Normal mode navigates token anchors; Edit mode owns a pending ASCII token.

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

