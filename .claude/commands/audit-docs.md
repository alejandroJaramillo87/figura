---
description: Audit a docs subtree against the tree and return a drift list
argument-hint: <docs-path>
---
Delegate to the doc-auditor subagent. Detection and repair are separate: doc-auditor reports
the drift, and doc-writer fixes it in a later pass.

Audit the documentation under `$ARGUMENTS` (default: `docs/`) against the source of truth:
`scripts/`, `shared/`, `templates/`, `manifest.json`, `package.json`, `tests/` and
`.github/workflows/validate.yml`.

Return a drift list only: `file:line: documented X, actual Y`. If there is no drift, say so.
