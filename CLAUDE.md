# CLAUDE.md — diagram generation contract

This repo is a library of animated/interactive technical diagrams for the
Curiosity Chronicles blog (LLM training, mech interp, inference engine
internals) and, for static diagrams, the ai-experiments docs site. Each
diagram is **one self-contained HTML file** built from SVG, scoped CSS, and
vanilla JS. The blog inlines the fragment into posts at build time through
a Hugo shortcode, so every file must follow the conventions below exactly. Existing diagrams under `diagrams/` are the style reference — read
one or two before writing a new one.

Detailed human-oriented documentation (architecture, blog integration,
development workflow, authoring guide) lives in `docs/` — see
`docs/README.md` for the index. This file remains the enforced contract.

## Workflow for generating a new diagram

1. Read the diagram notes provided by the author.
2. Read 1–2 existing diagrams closest in kind (step-timeline,
   hover-inspect, toggle, ambient or static).
3. Scaffold the file (this also appends the `manifest.json` entry —
   fill in its `description`):

   ```bash
   node scripts/new-diagram.js <consumer-dir>/<kebab-name> \
     --kind step-timeline|hover-inspect|toggle|ambient|static \
     --abbr <2-6 char prefix> --title "Human-readable title"
   ```

   `<consumer-dir>` names where the diagram is used: the blog post's
   filename stem, the series directory for a post in a series
   (`what-language-leaves-out/`), or the docs-site section for a static
   diagram (`rust-harness/`). Once a page embeds or copies the diagram,
   add it to the entry's `consumers` list as `<repo>:<path>`.
4. Author only the diagram-specific parts: the SVG (statically — never
   generate markup at runtime), the `is-step-N` / state CSS, the
   `STATES` or `CAPTIONS` table a toggle or captioned timeline reads,
   effect keyframes copied from `shared/effects.css` (renamed to the
   abbr), and any `fg:step` / `fg:toggle` / `fg:hover` handlers.
5. **Never edit inside `fg:begin <name> vN` / `fg:end <name>` sentinel
   blocks.** Those regions are owned by `scripts/build.js` and re-expanded
   from `shared/runtime/` and `shared/tokens.css`. Diagram-specific tuning
   uses the hook variables the blocks expose (`--fg-ctl-accent`,
   `--fg-cap-accent`, `--fg-cap-minh`) or additional rules outside the
   blocks.
6. Check: `node scripts/build.js --check && node scripts/validate.js`
   (also available as `npm run check`). The validator enforces the
   mechanical rules below plus manifest sync; the rules it cannot see
   (never animating filter primitives, effect taste, a meaningful
   `aria-label`) are checked in review.
7. Preview: open the file directly in a browser, and check the gallery
   (`python3 -m http.server`, open `index.html`) — the gallery renders the
   first manifest entry twice as a multi-instance regression check.

## Managed blocks (the shared runtime)

Boilerplate every diagram needs is not hand-copied; it lives once under
`shared/runtime/` and is stamped into each fragment between sentinel
comments (`/* fg:begin controls-bar v1 */ … /* fg:end controls-bar */` in
CSS, `// fg:begin timeline-core v1 … // fg:end timeline-core` in JS):

| block | provides |
|---|---|
| `palette-classic` | scoped palette vars, derived from `shared/tokens.css` (local names: `--bg`, `--accent`, `--ok-dim`, …), including the shared type/shape/motion tokens (`--font`, `--mono`, `--radius`, `--dur-quick`, `--dur-fast`, `--dur-slow`, `--ease`), plus zero-specificity `fg-fill-<token>` / `fg-stroke-<token>` classes that stand in for colour attributes |
| `panel-base` | panel background, radius, font, shadow, responsive `svg`/`text` base rules |
| `reduced-motion` | kill-all transitions/animations under `prefers-reduced-motion` (extra reduced-motion rules go in a second `@media` outside the block) |
| `controls-bar` | prev/play/next/counter bar styling (`--fg-ctl-accent` overrides hover color) |
| `timeline-core` | `tl` step state machine (`is-step-N`, `fg:step` events, `is-playing`), control wiring, `reduced` flag — expects `TOTAL` and `STEP_MS` consts above it |
| `timeline-start` | initial `apply()`, then the reduced-motion final-state jump, or autoplay once 30% visible that a reader's pause turns off — place after any `fg:step` listeners |
| `caption-box` | `.fg-caption` box (`--fg-cap-accent`, `--fg-cap-minh` hooks), the grid that reserves the tallest caption's height, and the focus ring for `data-info` targets |
| `caption-core` | `reserveCaption(variants)` and `setCaption(html)`: stacks every caption variant invisibly so the box never changes height, and announces changes through `aria-live` |
| `hover-caption` | `data-info` (plus optional `data-title`, `data-code`) → caption readout on hover and on keyboard focus; emits `fg:hover` `{ el, index, on }` |
| `step-caption` | renders `CAPTIONS[step]` (text, or `[title, text]`) into the caption on each `fg:step` |
| `toggle-bar` | toggle button bar styling, pressed state and focus ring |
| `toggle-core` | a `STATES` table (`{ cls, cap, label? }`) driven by one cycling `data-fg="toggle"` button or one button per state; `tg.show(n)`, `tg.next()`, `fg:toggle` events |
| `instance-ids` | in the second and later copies of a diagram on one page, suffixes ids and rewrites `href`, `url(#…)` and SMIL syncbase references — required wherever syncbase timing appears |

Each manifest `kind` requires a set of blocks, in dependency order.
Every kind carries `palette-classic`, `panel-base` and `reduced-motion`;
`step-timeline` adds `controls-bar`, `timeline-core` and
`timeline-start`; `hover-inspect` adds `caption-box`, `caption-core` and
`hover-caption`; `toggle` adds `toggle-bar`, `caption-box`,
`caption-core` and `toggle-core`. A block's version (`v1`) is its
interface version: it changes only when what the host diagram must
provide changes, and the validator refuses a stale one.

`node scripts/build.js` re-expands every block (idempotent); `--check`
fails if any block drifted from its canonical source. Palette changes are
made in `shared/tokens.css`, then `node scripts/build.js` propagates them
to every diagram in the library. CI (`.github/workflows/validate.yml`) runs
`build --check` and the validator on every push and PR.

## File anatomy

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Human-readable diagram title</title>
<link rel="stylesheet" href="../../shared/preview.css">  <!-- preview page chrome only -->
</head>
<body>
<h1>Title</h1>
<p>One-line description for standalone viewing.</p>

<!-- fg:embed-start -->
<div class="fg-diagram fg-<diagram-name>">
  <style>/* everything scoped under .fg-<diagram-name> */</style>
  <svg viewBox="0 0 W H" role="img" aria-label="...">…</svg>
  <!-- optional: .fg-caption box, .fg-controls bar -->
  <script>(() => {
    const root = document.currentScript.closest('.fg-diagram');
    /* query only within root */
  })();</script>
</div>
<!-- fg:embed-end -->
</body>
</html>
```

Only the fragment between `<!-- fg:embed-start -->` and `<!-- fg:embed-end -->`
is inlined into the blog. Everything the diagram needs must live inside it.

## Hard rules (the blog inlines this fragment into a busy page)

- **Scoping.** Root element carries `fg-diagram fg-<diagram-name>`, where
  `<diagram-name>` is the file stem. Every CSS selector is prefixed with
  `.fg-<diagram-name>`. No bare element selectors,
  no styling `body`/`html`, no global keyframe names (prefix: `fg-<abbrev>-*`).
- **Namespaced ids.** SVG ids (markers, gradients, clips) are document-global
  once inlined — prefix them per diagram (e.g. `kvcf-arrowhead`), and never
  reuse an id or keyframe name another diagram defines. If the same diagram
  appears twice on a page, duplicate marker ids resolve to the first
  instance's definition, which is fine because definitions are identical;
  SMIL syncbase timing is not, which is what `instance-ids` fixes.
- **No HTML comments** inside the fragment: the blog inlines it verbatim, so
  they ship to readers. Explain markup in the `<style>` or in the commit.
- **Tokens only.** No literal colours outside managed blocks: CSS uses the
  palette vars, and SVG colour attributes become `fg-fill-*` /
  `fg-stroke-*` classes. Transition durations use `--dur-quick` (hover),
  `--dur-fast` (state) or `--dur-slow` (draw-in); monospace text uses
  `var(--mono)`.
- **Scoped JS.** One bare `<script>` holding exactly one IIFE. Resolve the root via
  `document.currentScript.closest('.fg-diagram')` and query only within it.
  No globals, no `DOMContentLoaded` (the script sits after its markup), no
  `getElementById`.
- **Self-contained.** No external network requests: no webfonts, no CDN
  libraries, no linked CSS/JS, and no relative URLs (they resolve against
  the blog page) inside the fragment. Copy what you need from
  `shared/`. `preview.css` may only be linked from `<head>` (outside the
  fragment).
- **No absolute paths** anywhere in the file.
- **Motion.** Ambient CSS animations are fine. Step timelines autoplay only
  when ~30% visible (IntersectionObserver) and pause off-screen. Under
  `prefers-reduced-motion`: kill transitions/animations and jump step
  timelines to the final state (manual controls stay usable).
- **Accessibility.** `role="img"` + meaningful `aria-label` on the SVG;
  `aria-label` and `type="button"` on control buttons. Nothing inside the
  `role="img"` SVG takes `role="button"`: assistive technology cannot reach
  it. Interactive state is driven by real buttons in `.fg-controls`, and
  hover readouts are reachable by keyboard focus through `hover-caption`.
- **No layout shift.** Elements whose content changes at runtime must
  reserve their maximum height up front, so interacting with a diagram
  never reflows the surrounding post. Captions do this through
  `caption-core`, which sizes the box for the longest variant at any
  width; anything else sizes its own `min-height`.
- **Responsive.** SVG uses `viewBox` and `width: 100%; height: auto`. Design
  for a ~720px column; keep text ≥ 11px at natural size (the
  validator rejects smaller `font-size` values).
- **Static kind.** A diagram whose manifest entry says `"kind": "static"`
  carries no `<script>`, no SMIL element, no `@keyframes`, no `animation` or
  `transition` declaration outside the managed blocks, and no
  `.fg-controls` or `.fg-caption` markup. State is encoded with the palette
  hues, not motion. The kind exists for consumers that cannot inline HTML or
  run script: `node scripts/export-svg.js` writes each static diagram to
  `dist/<slug>/<name>.svg` as a standalone image, and the consuming repo
  commits a copy. The validator enforces all of it.

## Visual language

### Palette

One palette — **classic dark** (`--fg-*`, table below) — lives in
`shared/tokens.css` (copy values via the managed block, never link).
figura owns it: the blog mirrors eleven of these values for its code
panels, and its `tests/check-figura-tokens.mjs` fails until the mirror
matches, so a palette change lands here first. Dark slate panels read as
framed figures on the light theme and sit nearly flush on the dark theme. Diagrams
never theme-switch; the dark panel is correct on both page themes.

The live reference (all swatches + every effect) is
`diagrams/effects-sampler/effects-sampler.html`.

### Effects catalog

`shared/effects.css` is the copy-source catalog of animation patterns:
**glow, highlight sweep, comet, draw-in, pulse/ripple, shimmer, flash** —
each with markup, technique, and reduced-motion fallback. Rename the
`fg-XX-*` keyframe placeholders to the diagram's abbreviation when
copying. Additional hard rules that come with the effects:

- **Never animate SVG filter primitives.** Filters re-render per frame
  and jank. Blur a duplicate node once, statically; animate only its
  opacity (this is the glow pattern).
- **SMIL ignores `prefers-reduced-motion`.** Every SMIL element
  (`animate`, `animateMotion`, `animateTransform`, `set`) must sit inside
  an element hidden with CSS `display: none` under the reduced-motion
  media query — the CSS gate is mandatory, not optional.
- **Taste:** one lead effect per step, at most ~3 animated elements
  concurrently. Effects must explain (a comet shows direction, a glow
  shows activation, a ripple shows an in-place update) — decoration for
  its own sake reads as noise on a technical blog.

Step-triggered one-shots use `restartAnimation()` and `launchComets()`
from `shared/snippets.js` (comets authored with `begin="indefinite"`,
kicked from the `fg:step` handler; trails chain off the head via
syncbase timing, e.g. `begin="xx-head.begin+0.1s"`, which requires the
`instance-ids` block).

### Classic dark tokens

Dark slate panel on the blog's light page:

| token | value | use |
|---|---|---|
| `--bg` | `#0f172a` | panel background |
| `--panel` | `#1e293b` | blocks, cells |
| `--panel-hover` | `#334155` | hover fill |
| `--border` | `#334155` | strokes |
| `--text` | `#f8fafc` | primary labels |
| `--muted` | `#94a3b8` | secondary labels |
| `--accent` | `#38bdf8` | highlights, active flow |
| `--ok` | `#34d399` | filled / cached / residual |
| `--warn` | `#fbbf24` | in-progress / decode / hot path |
| `--hot` | `#f87171` | bottleneck / eviction |
| `--violet` | `#a78bfa` | secondary series |
| `--accent-dim` / `--ok-dim` / `--warn-dim` / `--hot-dim` / `--violet-dim` | `#0c3550` / `#0e4429` / `#4a3608` / `#4a1d1d` / `#2a2350` | `is-step-N` active box fills (accent hue ~15% over panel) — never hand-mix these |
| `--line` | `#64748b` | connectors, arrowheads |

Easing and durations always come from the palette block: `var(--ease)`,
and `var(--dur-quick)` (0.3s hover feedback), `var(--dur-fast)` (0.45s
state transitions) or `var(--dur-slow)` (0.7s draw-in). Timeline cadence
is set per diagram by the `STEP_MS` const the `timeline-core` block
reads. The validator rejects literal `cubic-bezier()`, literal colours,
hand-mixed dim hexes and literal transition durations outside managed
blocks.

Font: `"Work Sans", system-ui, -apple-system, "Segoe UI", sans-serif`
(system fallback — never fetch webfonts). Rounded corners (12px panel),
`cubic-bezier(0.4, 0, 0.2, 1)`.

Interaction patterns, one per kind:
- **Step timeline** — root class `is-step-N` drives CSS states; prev/play/next
  controls; good for loops, cache fills, pipelines.
- **Hover-to-inspect** — blocks carry `data-info`; a `.fg-caption` box below
  the SVG shows details; good for architecture block diagrams.
- **Toggle** — a button flips or cycles the root through `STATES`, each with
  its caption; good for two readings of one sentence.
- **Ambient flow** — dashed `stroke-dasharray` lines with a `stroke-dashoffset`
  keyframe animation for data flowing along paths.

## Embedding in the blog

The blog repo mounts this repo as a git submodule at `static/diagrams` and
provides a shortcode:

```text
{{</* diagram name="inference-loop/kv-cache-fill" caption="..." */>}}
```

After changes merge here, the blog picks them up only when its submodule
pointer moves. Run the blog's `/bump-figura` command there: it moves the
pointer, runs the blog's `npm run quality` gate, and reports what changed.
A consumer of a static diagram (the ai-experiments docs site) re-copies
the SVG from `node scripts/export-svg.js` instead.
