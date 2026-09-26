---
description: Audit diagrams against the review-only contract rules and their consumer pages
argument-hint: <diagrams/slug or path>
---
Delegate to the diagram-auditor subagent for the diagrams under `$ARGUMENTS` (default: every
diagram changed on this branch, from `git diff --name-only main -- diagrams/`).

Return its findings only. Do not fix anything; diagram-author does that in a later pass.
