# Development

## Prerequisites

- Node.js at the exact version in `.nvmrc` (`nvm use`). The gate refuses
  any other version. The checks use only Node built-ins, so
  `npm run quality` has no install step. `npm run quality:full` adds the
  browser tier, which needs `npm ci` (for the pinned `playwright-core`)
  and a Chromium at `PLAYWRIGHT_CHROMIUM`, or `/opt/pw-browsers/chromium`.
- Python 3 (optional) for serving the gallery locally
  (`python3 -m http.server`). Nothing in the tooling needs it.

## Creating a diagram

Scaffold with the CLI (`npm run new -- …` or directly):

```bash
node scripts/new-diagram.js <consumer-dir>/<kebab-name> \
  --kind step-timeline|hover-inspect|toggle|ambient|static \
  --abbr <2-6 char prefix> --title "Name: what it shows"
```

This checks every input first, then copies the matching
`templates/<kind>.html` with the name/title/abbr substituted, expands
the managed blocks, writes the file to
`diagrams/<consumer-dir>/<kebab-name>.html`, and appends a
`manifest.json` entry whose `description` is a TODO you must fill in
and whose `consumers` list starts empty. The validator refuses the TODOs
until they are gone. Pick the kind with the guidance in
[authoring.md](authoring.md#choosing-a-kind).

Then author the diagram-specific parts: the static SVG, the
`is-step-N` or state CSS, the `STATES` or `CAPTIONS` table the kind
reads, effect keyframes copied from `shared/effects.css` (renamed to
your abbr), and any custom `fg:step` / `fg:toggle` / `fg:hover`
handlers. Follow the contract in [CLAUDE.md](../CLAUDE.md); read 1–2
existing diagrams of the same kind first.

## Editing rules

- **Never edit inside `fg:begin … / fg:end …` sentinel blocks.** They
  are owned by `scripts/build.js`; hand edits are reverted by the next
  `build` run and fail `--check` until then. Tune via the hook
  variables (`--fg-ctl-accent`, `--fg-cap-accent`, `--fg-cap-minh` —
  hooks the blocks expose, whether or not any diagram sets them) or
  add rules outside the blocks.
- **Palette and shared-boilerplate changes** go in `shared/tokens.css`
  or `shared/runtime/`, then propagate repo-wide:

  ```bash
  node scripts/build.js        # rewrites every diagram's managed blocks
  ```

  Palette values are mirrored from the blog's design tokens — see
  [blog-integration.md](blog-integration.md#shared-design-language)
  before changing them.

## Checking

```bash
npm run check   # = node scripts/build.js --check && node scripts/validate.js
```

`build.js --check` fails if any managed block drifted from its
canonical source; `validate.js` lints every diagram against the
contract.

### What the validator enforces

Per file: exactly one pair of embed markers; well-formed sentinels
(`sentinel`); the managed blocks the manifest kind requires, each once,
at its canonical version and after the blocks it depends on
(`block-required`, `block-duplicate`, `block-version`, `block-order`);
a root element carrying `fg-diagram fg-<file stem>`; every CSS selector
scoped under the root class, including inside `@media`, `@supports`,
`@container` and `@layer`; keyframes `fg-<abbr>-*` prefixed; no id or
keyframe name that another diagram also defines (`global-name`); no
`<link>`, `@import`, external `script src`, external or relative URLs,
or absolute paths inside the fragment; no HTML comments; no literal
`cubic-bezier()`, colour, hand-mixed dim hex, or transition duration
outside managed blocks; no `font-size` below 11px and no hand-written
monospace stack; `prefers-reduced-motion` handling present, with every
SMIL element inside an element that a reduced-motion `display: none`
rule hides; the `instance-ids` block wherever SMIL syncbase timing
appears; SVG ids diagram-prefixed and all id references resolvable
within the fragment; `role="img"` + `aria-label` on every `<svg>`; no
leftover scaffold `TODO`; scripts that are a bare `<script>` holding one
IIFE, resolve their root via `document.currentScript.closest`, avoid
`getElementById`/`DOMContentLoaded`, and parse cleanly. A diagram the
manifest marks `static` additionally has no `<script>`
(`static-script`), no SMIL element (`static-smil`), no `@keyframes` and
no `animation`/`transition` declaration outside managed blocks
(`static-motion`), and no `.fg-controls`/`.fg-caption` markup
(`static-chrome`).

Per repo: manifest entries have all six fields (`id`, `path`,
`title`, `kind`, `consumers`, `description`), a known `kind`, consumers
written as `<repo>:<path>`, a filled description, unique ids and paths,
`id` equal to the filename stem, a title in curly quotes that the page's
`<title>` and `<h1>` repeat exactly, every path existing, and no diagram
missing from the manifest.

`node scripts/validate.js --warn` reports the same findings but exits
0, which is useful mid-refactor.

## Previewing

- **Single diagram:** open its HTML file directly — `file://` works,
  since each file is standalone.
- **Gallery:** `python3 -m http.server 8000` in the repo root, then
  <http://localhost:8000/>. HTTP is required (the gallery fetches
  `manifest.json`, which fails under `file://`). The gallery renders
  the first manifest entry twice as a multi-instance collision check —
  glance at it when touching anything shared.
- Check both with and without OS reduced-motion enabled if you touched
  animation.

## CI

`.github/workflows/validate.yml` runs `node tests/quality.mjs` (the same
command as `npm run quality`) on every push to `main` and every pull
request, on the Node version in `.nvmrc`. Its actions are pinned by commit
SHA, the token is read-only, and a newer push to a pull request cancels
the stale run.

## Troubleshooting

- **`--check` fails with block drift** — someone edited inside a
  sentinel block, or `shared/runtime/`/`tokens.css` changed without a
  `build` run. Run `node scripts/build.js` and diff: if your edit
  disappeared, move it outside the block or into the canonical source.
- **`css-scope` findings** — a selector does not start with
  `.fg-<name>`. Prefix it; there are no legitimate unscoped selectors
  inside a fragment.
- **`id-ref` findings** — an SVG `url(#…)`/`href="#…"`/`begin="…"`
  points at an id not defined in the same fragment; typically a typo
  or a leftover from a copied effect.
- **`smil-gate` findings** — a SMIL element that no `display: none`
  rule under the reduced-motion media query hides. The CSS gate is
  mandatory because SMIL ignores `prefers-reduced-motion`.
- **`sentinel` findings** — a `fg:begin` or `fg:end` comment that is
  malformed, unclosed, nested or mismatched. Fix the marker; `build.js`
  refuses to touch the file until it pairs.
- **`manifest` findings** — usually a diagram added or renamed without
  updating `manifest.json` (the scaffolder appends entries; manual
  renames must be mirrored by hand).
