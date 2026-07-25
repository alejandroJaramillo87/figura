# Development

## Prerequisites

- Node.js >= 18. That's it — the tooling is zero-dependency, so there
  is no `npm install` step (`package.json` has no dependencies).
- Python 3 (optional) for serving the gallery locally.

## Creating a diagram

Scaffold with the CLI (`npm run new -- …` or directly):

```bash
node scripts/new-diagram.js <post-slug>/<kebab-name> \
  --kind step-timeline|hover-inspect|ambient|hero \
  --abbr <2-6 char prefix> --title "Human-readable title"
```

This copies the matching `templates/<kind>.html` with the name/title/
abbr substituted, expands the managed blocks, writes the file to
`diagrams/<post-slug>/<kebab-name>.html`, and appends a
`manifest.json` entry — whose `description` is a TODO you must fill
in. Pick the kind with the guidance in
[authoring.md](authoring.md#choosing-a-kind).

Then author the diagram-specific parts: the static SVG, the
`is-step-N` state CSS, effect keyframes copied from
`shared/effects.css` (renamed to your abbr), and any custom `fg:step`
handlers. Follow the contract in [CLAUDE.md](../CLAUDE.md); read 1–2
existing diagrams of the same kind first.

## Editing rules

- **Never edit inside `fg:begin … / fg:end …` sentinel blocks.** They
  are owned by `scripts/build.js`; hand edits are reverted by the next
  `build` run and fail `--check` until then. Tune via the hook
  variables (`--fg-ctl-accent`, `--fg-cap-accent`, `--fg-cap-minh`) or
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

Per file: embed markers present and balanced; root element carries
`fg-diagram fg-<name>`; every CSS selector scoped under the root
class; keyframes `fg-<abbr>-*` prefixed; no `<link>`, `@import`,
external `script src`, external URLs, or absolute paths inside the
fragment; no literal `cubic-bezier()` or hand-mixed dim hexes outside
managed blocks; `prefers-reduced-motion` handling present, with a
`display: none` gate whenever `<animateMotion>` (SMIL) is used; SVG
ids diagram-prefixed and all id references resolvable within the
fragment; `role="img"` + `aria-label` on every `<svg>`; scripts
resolve their root via `document.currentScript.closest`, avoid
`getElementById`/`DOMContentLoaded`, and parse cleanly.

Per repo: manifest entries have all five fields, unique ids/paths,
`id` == filename stem, every path exists, and no diagram is missing
from the manifest.

`node scripts/validate.js --warn` reports the same findings but exits
0 — useful mid-refactor. `validate.js` also has an `EXEMPT` map for
per-file rule exemptions (currently empty; use sparingly).

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

`.github/workflows/validate.yml` runs `node scripts/build.js --check`
and `node scripts/validate.js` (the same commands as `npm run check`)
on every push to `main` and every pull request, on Node 22.

## Troubleshooting

- **`--check` fails with block drift** — someone edited inside a
  sentinel block, or `shared/runtime/`/`tokens.css` changed without a
  `build` run. Run `node scripts/build.js` and diff: if your edit
  disappeared, move it outside the block or into the canonical source.
- **`css-scope` findings** — a selector doesn't start with
  `.fg-<name>`. Prefix it; there are no legitimate unscoped selectors
  inside a fragment.
- **`id-ref` findings** — an SVG `url(#…)`/`href="#…"`/`begin="…"`
  points at an id not defined in the same fragment; typically a typo
  or a leftover from a copied effect.
- **`smil-gate` findings** — a `<animateMotion>` comet without a
  `display: none` rule under the reduced-motion media query. The CSS
  gate is mandatory because SMIL ignores `prefers-reduced-motion`.
- **`manifest` findings** — usually a diagram added or renamed without
  updating `manifest.json` (the scaffolder appends entries; manual
  renames must be mirrored by hand).
