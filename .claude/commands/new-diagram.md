---
description: Scaffold, author and gate a new diagram from the author's notes, then stop for review
argument-hint: <consumer-dir>/<kebab-name> <kind>
---
Delegate to the diagram-author subagent to create `diagrams/$ARGUMENTS` from the diagram notes
in this conversation.

1. Scaffold it with `npm run new`, fill in the manifest description, and add the consumer page
   to `consumers` once the author names it.
2. Author the diagram-specific parts only, following `.styles/DIAGRAM_STYLE.md`.
3. Run `npm run quality:full`.
4. Stop. Report the file, the gate's last line, and anything in the notes left undecided. Do
   not commit; the author reviews the diagram in the gallery first.
