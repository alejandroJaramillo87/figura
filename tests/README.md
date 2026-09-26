# Tests

The quality gate and the checks it runs, beyond the validator in `scripts/`: retired names,
code blocks, links, contract citations, generated docs and the browser tier.

<!-- inventory:dirs:start -->

| Directory | Holds |
|-----------|-------|
| [lib/](lib/README.md) | Plumbing the checks share: the repository root, the tracked-file list and the report format. |

<!-- inventory:dirs:end -->

<!-- inventory:pages:start -->

| File | Holds |
|------|-------|
| [check-command-prompts.mjs](check-command-prompts.mjs) | Code blocks in repository markdown name their language, and shell blocks carry no prompt marker. |
| [check-contract.mjs](check-contract.mjs) | The contract and the validator cite each other honestly. |
| [check-links.mjs](check-links.mjs) | Internal links in repository markdown resolve. |
| [check-retired-names.mjs](check-retired-names.mjs) | Retired paths stay retired. |
| [docs.mjs](docs.mjs) | Generate, or with --check verify, the derived parts of the repository's markdown: the router tables in every README, the roster tables over the style guides, agents and commands, and the tables of contents in long documents. |
| [quality.mjs](quality.mjs) | The quality gate: every check a push must pass, in one command. |
| [render.test.mjs](render.test.mjs) | Browser checks for what the validator cannot see: every diagram renders without a script error or a failed request, never changes height while a reader drives it, and jumps a step timeline to its final state under reduced motion. |

<!-- inventory:pages:end -->

`npm run quality` runs everything here except `render.test.mjs`, which `npm run quality:full`
adds. See [docs/testing/quality-gate.md](../docs/testing/quality-gate.md).
