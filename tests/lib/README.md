# Test library

Plumbing the checks share: the repository root, the tracked-file list and the report format.

<!-- inventory:pages:start -->

| File | Holds |
|------|-------|
| [check.mjs](check.mjs) | Shared plumbing for the tests/check-*.mjs gates: the repository root, the tracked-file list, and the report format scripts/lib/report.js also uses, so every step of `npm run quality` reads the same. |

<!-- inventory:pages:end -->
