# Architecture

figura is a library of animated technical diagrams built to be inlined
into blog posts at build time. That single constraint — a fragment of
HTML dropped verbatim into a busy page, possibly twice — drives every
architectural decision below.

## The one-file-per-diagram model

Each diagram is **one self-contained HTML file** under
`diagrams/<post-slug>/<kebab-name>.html`, built from three parts:

- a static SVG (markup is authored, never generated at runtime),
- scoped CSS in a `<style>` tag,
- vanilla JS in a single IIFE.

The file is also a standalone page you can open directly in a browser:
the `<head>` links `shared/preview.css` for page chrome, and the body
carries a title and one-line description. But only the region between
the markers

```html
<!-- fg:embed-start -->
<div class="fg-diagram fg-<diagram-name>"> … </div>
<!-- fg:embed-end -->
```

is consumed by the blog. Everything the diagram needs at embed time —
styles, markup, script — must live inside that fragment; everything
outside it (including the `preview.css` link) exists only for
standalone viewing.

Self-containment is why the hard rules in [CLAUDE.md](../CLAUDE.md)
exist: CSS scoped under the root class, `fg-<abbr>-*` keyframe
prefixes, per-diagram SVG id prefixes, JS that resolves its root via
`document.currentScript.closest('.fg-diagram')`, and no external
requests of any kind. Once inlined, ids and keyframe names are
document-global and the script runs in the page's scope; the
conventions are what keep two diagrams — or two copies of the *same*
diagram — from colliding.

## Directory layout

```
diagrams/<post-slug>/<name>.html   the diagrams (one dir per blog post)
templates/                         scaffolds: step-timeline, hover-inspect, ambient, hero
shared/
  tokens.css                       palette source of truth (classic dark)
  runtime/                         canonical managed-block sources
  effects.css                      copy-source catalog of animation effects
  snippets.js                      reference-only JS patterns
  preview.css                      standalone/gallery page chrome (never inlined)
scripts/
  new-diagram.js                   scaffolder
  build.js                         managed-block expander / drift checker
  validate.js                      contract linter
  lib/fragment.js                  shared parsing helpers used by all three
manifest.json                      diagram index
index.html                         gallery
```

## Managed blocks — the core mechanism

Every diagram needs the same boilerplate: palette variables, panel
styling, control-bar styling, the step-timeline state machine, and so
on. Rather than hand-copying it (and watching 68 copies drift), the
canonical source of each piece lives once under `shared/runtime/`, and
`scripts/build.js` stamps it into every fragment between sentinel
comments:

```css
/* fg:begin controls-bar v1 */
…generated, do not edit…
/* fg:end controls-bar */
```

```js
// fg:begin timeline-core v1
…generated, do not edit…
// fg:end timeline-core
```

The blocks (see the table in [CLAUDE.md](../CLAUDE.md) for what each
provides):

| block | source |
|---|---|
| `palette-classic` | derived from `shared/tokens.css` |
| `panel-base` | `shared/runtime/panel-base.css` |
| `controls-bar` | `shared/runtime/controls-bar.css` |
| `caption-box` | `shared/runtime/caption-box.css` |
| `reduced-motion` | `shared/runtime/reduced-motion.css` |
| `timeline-core` | `shared/runtime/timeline-core.js` |
| `timeline-start` | `shared/runtime/timeline-start.js` |
| `hover-caption` | `shared/runtime/hover-caption.js` |

Properties of the system:

- **Idempotent expansion.** `node scripts/build.js` rewrites every
  block body from its canonical source (re-indented to match the begin
  marker); running it twice is a no-op. `--file <path>` limits it to
  one diagram.
- **Drift detection.** `node scripts/build.js --check` writes nothing
  and exits non-zero if any block body differs from canonical, or an
  unknown block name appears. CI runs this on every push and PR, so a
  hand-edited block cannot land.
- **One edit propagates everywhere.** Change `shared/tokens.css` (or a
  runtime file), run `build.js`, and every diagram picks it up.
- **Customization goes through hooks, not edits.** Blocks expose CSS
  hook variables (`--fg-ctl-accent`, `--fg-cap-accent`,
  `--fg-cap-minh`) that a diagram sets *outside* the sentinels;
  anything else diagram-specific also lives outside the blocks.

`shared/snippets.js` documents the JS patterns for humans; the
executable truth is `shared/runtime/`.

## The scripts pipeline

All three CLIs sit on `scripts/lib/fragment.js`, the shared parsing
layer: splitting a file on the embed markers (`splitEmbed`), finding
the root class (`rootClass`), locating sentinel blocks (`findBlocks`),
generating the palette block from `tokens.css`, listing diagram files,
and loading the manifest.

- **`scripts/new-diagram.js`** (`npm run new`) scaffolds a diagram:
  validates the `<slug>/<name>` and `--abbr`, copies
  `templates/<kind>.html` with `{{NAME}}`/`{{TITLE}}`/`{{ABBR}}`/…
  substitution, expands the managed blocks via `build.js --file`, and
  appends a `manifest.json` entry with a TODO description.
- **`scripts/build.js`** (`npm run build`) is the block expander
  described above.
- **`scripts/validate.js`** (`npm run validate`) is the contract
  linter — it mechanically enforces the CLAUDE.md hard rules plus
  manifest sync. See [development.md](development.md#what-the-validator-enforces)
  for the rule list.

The code is structured for multiple palettes (`--palette` on the
scaffolder, palette maps in `fragment.js`), but only `classic` is
wired — one dark palette is a deliberate choice, since diagrams never
theme-switch on the blog.

## manifest.json

A flat array indexing every diagram:

```json
{ "id": "kv-cache-fill",
  "path": "diagrams/inference-loop/kv-cache-fill.html",
  "title": "KV cache fill during decode",
  "post": "inference-loop",
  "description": "…" }
```

The validator enforces: all five fields present, ids and paths unique,
`id` equal to the filename stem, every `path` existing on disk, and no
diagram on disk missing from the manifest. `post` names the blog post
the diagram belongs to; entries for not-yet-published posts use
placeholder values (e.g. `"future — LLM training series"`, or
`"n/a — internal reference"` for the effects sampler).

## The gallery (`index.html`)

A dependency-free page that fetches `manifest.json`, extracts each
file's embed fragment with the same marker convention, injects the
markup, and re-creates the `<script>` nodes so they execute. It
renders the **first manifest entry twice** as a standing regression
check for multi-instance collisions — exactly the situation a blog
post embedding the same diagram twice would create. Because of the
manifest fetch it must be served over HTTP
(`python3 -m http.server`), not opened via `file://`.
