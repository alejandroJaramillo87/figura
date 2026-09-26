# Development workflow

The day-to-day commands for working in figura: prerequisites, creating and checking a diagram,
previewing, what CI runs, and how to recover from the common failures. What each gate step
checks is in [the quality gate](../testing/quality-gate.md), and the rules a diagram follows are
in [.styles/DIAGRAM_STYLE.md](../../.styles/DIAGRAM_STYLE.md).

## Table of Contents

<!-- toc:start -->

1. [Prerequisites](#prerequisites)
2. [Commands](#commands)
3. [Creating a diagram](#creating-a-diagram)
4. [Changing shared code](#changing-shared-code)
5. [Previewing](#previewing)
6. [CI](#ci)
7. [Troubleshooting](#troubleshooting)

<!-- toc:end -->

## Prerequisites

- Node at the exact version in `.nvmrc` (`nvm use`). The gate refuses any other version. The
  checks use only Node built-ins, so `npm run quality` needs no install step.
- For `npm run quality:full`, the browser tier: `npm ci` for the pinned `playwright-core`, and
  a Chromium at `PLAYWRIGHT_CHROMIUM`, or `/opt/pw-browsers/chromium` by default.
- Python 3, optionally, to serve the gallery. Nothing in the tooling needs it.

## Commands

`package.json` lists the npm scripts:

| Command | What it does |
|---------|--------------|
| `npm run new -- <args>` | Scaffold a diagram and its manifest entry (`scripts/new-diagram.js`) |
| `npm run build` | Rewrite every managed block from its source |
| `npm run check` | The fast authoring loop: block drift, then the validator |
| `npm run validate` | The validator alone; add `-- --warn` to report without failing |
| `npm run export` | Rewrite every static diagram's SVG under `exports/` |
| `npm run quality` | The gate every push passes |
| `npm run quality:full` | The gate plus the browser tier |
| `npm run docs` | Regenerate README tables, tables of contents and rosters |

## Creating a diagram

Follow the [workflow for a new diagram](../../.styles/DIAGRAM_STYLE.md#workflow-for-a-new-diagram),
and pick the kind with the [authoring guide](../authoring/guide.md#choosing-a-kind). The
scaffolder checks every input first, then fills `templates/<kind>.html`, expands the managed
blocks, writes `diagrams/<consumer-dir>/<kebab-name>.html`, and appends a manifest entry whose
`description` is a TODO and whose `consumers` list starts empty. The validator fails until the
TODOs are gone.

Run `npm run check` while authoring. For a static diagram, run `npm run export` and commit the
changed file under `exports/`.

## Changing shared code

- **Never edit inside a sentinel block.** `scripts/build.js` owns it: the next `npm run build`
  reverts a hand edit, and `build --check` fails until then. Tune a diagram with the hook
  variables a block exposes, or with rules outside the block.
- **Change a palette value or a block in its source**, `shared/tokens.css` or
  `shared/runtime/`, then propagate it:

  ```bash
  npm run build
  ```

  A token change has consumer follow-ups; read [tokens.md](../consumers/tokens.md) first.

## Previewing

- **One diagram:** open its HTML file directly. `file://` works, because each file is
  standalone.
- **The gallery:** serve the repository root over HTTP, then open <http://localhost:8000/>.
  The gallery fetches `manifest.json`, which fails under `file://`.

  ```bash
  python3 -m http.server 8000
  ```

  The gallery renders the first manifest entry twice as a multi-instance check; look at it
  after touching anything shared.
- **Reduced motion:** after touching animation, view the diagram with the operating system's
  reduced-motion setting both on and off.

`npm run quality:full` repeats these checks in a headless browser, but it does not replace a
look: it catches errors and height changes, not a diagram that reads badly.

## CI

`.github/workflows/validate.yml` runs on every push to `main` and every pull request, on the
Node version in `.nvmrc`, with actions pinned by commit SHA and a read-only token. A newer push
to a pull request cancels its stale run. It has two jobs:

- **`quality`** runs `node tests/quality.mjs`, the same command as `npm run quality`.
- **`render`** runs `npm ci`, then `tests/render.test.mjs` against the runner's preinstalled
  Chrome. It is the only job that installs anything.

## Troubleshooting

Each validator finding names its rule id; the [rule list](../testing/quality-gate.md#validator-rules)
says what each one requires.

- **`managed blocks` step fails with drift.** Someone edited inside a sentinel block, or a
  source under `shared/` changed without a build. Run `npm run build` and diff: if an edit
  disappeared, move it outside the block or into the source.
- **`css-scope`.** A selector does not start with `.fg-<name>`. Prefix it; no selector inside
  a fragment is legitimately unscoped.
- **`id-ref`.** A `url(#...)` or `href="#..."` names an id the fragment does not define,
  usually a typo or a leftover from a copied effect.
- **`smil-gate`.** A SMIL element sits outside every element that the reduced-motion
  `display: none` rule hides.
- **`sentinel`.** A `fg:begin` or `fg:end` comment is malformed, unclosed, nested or
  mismatched. Fix the marker; `build.js` refuses the file until it pairs.
- **`manifest`.** A diagram was added or renamed without updating `manifest.json`. The
  scaffolder appends entries, but a rename is mirrored by hand, and a renamed file also goes
  into `RETIRED` in `tests/check-retired-names.mjs`.
- **`exports` step fails.** A static diagram changed without a re-export. Run
  `npm run export` and commit the result.
