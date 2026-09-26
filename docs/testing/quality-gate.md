# Quality gate

What `npm run quality` and `npm run quality:full` run, step by step, how each step reports, and
how to read a failure. `npm run quality` is the gate every push passes and the command CI runs;
`tests/quality.mjs` owns the step list, and this document explains it.

## Table of Contents

<!-- toc:start -->

1. [Two tiers](#two-tiers)
2. [Preflights](#preflights)
3. [Steps](#steps)
4. [The browser tier](#the-browser-tier)
5. [The report line](#the-report-line)
6. [CI](#ci)
7. [Reading a failure](#reading-a-failure)
8. [Validator rules](#validator-rules)

<!-- toc:end -->

## Two tiers

| Command | Runs | Needs |
|---------|------|-------|
| `npm run quality` | The preflights, then every static step | Node at the `.nvmrc` version, nothing installed |
| `npm run quality:full` | The same, plus the browser tier | `npm ci` for `playwright-core`, and a Chromium |

`npm run check` (block drift and the validator) is the fast loop while authoring. It is a
subset of the gate, not a substitute for it.

## Preflights

Two checks run before any step and stop the gate at once, because a run that passes them
cannot mean what CI means:

- **Node version.** The running Node must equal the version in `.nvmrc` exactly. The fix is
  `nvm use`.
- **Dependency without a lockfile.** If `package.json` declares any dependency and there is no
  `package-lock.json`, that dependency is unpinned. The fix is to pin exact versions and commit
  the lockfile.

## Steps

Every step runs even after one fails, so one run reports everything. In order:

| Step | Command | Fails when |
|------|---------|------------|
| `managed blocks` | `node scripts/build.js --check` | A managed block differs from its source, is unknown, or has a malformed sentinel |
| `validator` | `node scripts/validate.js` | A diagram or the manifest breaks a rule in the [rule list](#validator-rules) |
| `contract citations` | `node tests/check-contract.mjs` | A validator rule id goes uncited in the contract, the contract cites an id that does not exist, or a file outside the routers points at the agent import file instead of the document that owns the fact |
| `exports` | `node scripts/export-svg.js --check` | A committed file under `exports/` differs from a fresh export |
| `retired names` | `node tests/check-retired-names.mjs` | A tracked file still names a path in its `RETIRED` table, or names an `npm run` script that `package.json` does not define |
| `code blocks` | `node tests/check-command-prompts.mjs` | A code fence has no language, or a shell block carries a `$ ` prompt (a transcript is tagged `console` instead) |
| `links` | `node tests/check-links.mjs` | A relative link, or a backticked repository path, does not resolve |
| `render (browser)` | `node tests/render.test.mjs` | Only under `quality:full`; see [the browser tier](#the-browser-tier) |

Without `--full`, the gate prints a `[SKIP]` line for the browser tier, so a reader of the output
sees that it did not run. The gate ends with `N/M steps passed` and the names of the failed
steps, and exits nonzero if any failed.

The checks under `tests/` read git-tracked files only, so scratch output left in the tree never
reaches them. A new file is checked once it is tracked.

## The browser tier

`tests/render.test.mjs` serves the repository from a local static server (the gallery's
manifest fetch fails over `file://`) and drives a headless Chromium through the pinned
`playwright-core`. It checks what the validator cannot see:

- Every manifest entry loads at the blog's column width and at phone width without a script
  error, a console error, a failed request or an HTTP error.
- No diagram changes height while its controls, toggles and hover targets are driven, with
  autoplay paused first.
- Under reduced motion, every step timeline shows its final step.
- The gallery embeds every entry, and the first one twice, without an error.

The browser is `PLAYWRIGHT_CHROMIUM`, or `/opt/pw-browsers/chromium` when that is unset.

## The report line

Every check ends with one line in the same format, printed by `tests/lib/check.mjs` for the
checks under `tests/` and by `scripts/lib/report.js` for the scripts:

```text
PASS  links: 42 checked, 0 failed
```

Each failure prints above it on its own line, prefixed `FAIL`. A check that examined nothing
fails, even with no findings: an input pattern that stopped matching would otherwise report
`PASS` forever while checking nothing.

## CI

`.github/workflows/validate.yml` runs two jobs on every push to `main` and every pull request,
on the `.nvmrc` Node version, with actions pinned by commit SHA:

- **`quality`** runs `node tests/quality.mjs`, installing nothing.
- **`render`** runs `npm ci`, then `tests/render.test.mjs` against the runner's preinstalled
  Chrome.

## Reading a failure

1. Read the summary at the end for the failed step names.
2. Scroll up to that step's `== <name>` header, and read its `FAIL` lines. Each names a file
   and, for the validator, a rule id.
3. Rerun that step's command alone from the [steps table](#steps) while fixing it, then rerun
   the whole gate.

The [troubleshooting list](../development/workflow.md#troubleshooting) covers the common
findings.

## Validator rules

`scripts/validate.js` declares every rule id it reports in its `RULES` table, and
[DIAGRAM_STYLE.md](../../.styles/DIAGRAM_STYLE.md) cites each id beside the hard rule it
enforces. `npm run docs` renders this list from the table.

<!-- inventory:rules:start -->

| Rule | Fails unless |
|------|--------------|
| `embed-markers` | exactly one fg:embed-start / fg:embed-end pair, in order |
| `sentinel` | managed-block sentinels are well formed, paired and not nested |
| `block-unknown` | every managed block names a source under shared/runtime/ or the palette |
| `block-version` | every managed block carries its canonical interface version |
| `block-required` | the fragment carries every block its manifest kind requires |
| `block-order` | required blocks appear in dependency order |
| `block-duplicate` | no managed block appears twice |
| `root-class` | the root element carries fg-diagram fg-<file stem> |
| `css-scope` | every selector, including inside at-rules, starts with the root class |
| `keyframes` | keyframe names carry the fg-<abbr>- prefix |
| `global-name` | no keyframe name or SVG id is defined by another diagram |
| `id-prefix` | SVG ids carry a per-diagram prefix |
| `id-ref` | every url(#id) and href="#id" names an id the fragment defines |
| `instance-ids` | SMIL syncbase timing requires the instance-ids block |
| `js-scope` | one bare <script> holding one IIFE, rooted at currentScript, with no globals, DOMContentLoaded or getElementById |
| `js-syntax` | every script parses |
| `self-contained` | no external or relative URLs, imports, linked CSS or JS, or webfonts |
| `absolute-path` | no absolute filesystem paths |
| `html-comment` | no HTML comments inside the fragment |
| `color-token` | no literal colours outside managed blocks |
| `dim-token` | active fills use the --*-dim tokens, never hand-mixed hexes |
| `motion-token` | easing and transition durations come from palette tokens |
| `font-token` | monospace text uses var(--mono) |
| `font-size` | no font-size below 11px |
| `reduced-motion` | a prefers-reduced-motion rule covers the fragment |
| `smil-gate` | every SMIL element sits inside an element hidden under reduced motion |
| `a11y` | the SVG carries role="img" and an aria-label |
| `static-script` | a static diagram carries no script |
| `static-smil` | a static diagram carries no SMIL element |
| `static-motion` | a static diagram carries no keyframes, animation or transition outside managed blocks |
| `static-chrome` | a static diagram carries no controls or caption markup |
| `scaffold` | no TODO left in the fragment, and no unfilled manifest description |
| `title` | the page <title> and <h1> match the manifest title, which uses typographic quotes |
| `manifest` | manifest.json and diagrams/ list the same files, with every required field |
| `manifest-id` | a manifest id equals its file stem |

<!-- inventory:rules:end -->
