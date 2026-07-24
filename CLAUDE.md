# CLAUDE.md — diagram generation contract

This repo is a library of animated/interactive technical diagrams for the
Curiosity Chronicles blog (LLM training, mech interp, inference engine
internals). Each diagram is **one self-contained HTML file** built from SVG,
scoped CSS, and vanilla JS. Diagrams are inlined into blog posts at build
time by a Hugo shortcode, so every file must follow the conventions below
exactly. Existing diagrams under `diagrams/` are the style reference — read
one or two before writing a new one.

## Workflow for generating a new diagram

1. Read the diagram notes provided by the author.
2. Read 1–2 existing diagrams closest in kind (step-timeline vs hover-inspect).
3. Scaffold the file (this also appends the `manifest.json` entry —
   fill in its `description`):

   ```
   node scripts/new-diagram.js <post-slug>/<kebab-name> \
     --kind step-timeline|hover-inspect|ambient \
     --palette classic|pastel-dark|pastel-light \
     --abbr <2-6 char prefix> --title "Human-readable title"
   ```

   `<post-slug>` matches the blog post's filename stem in `content/posts/`.
4. Author only the diagram-specific parts: the SVG (statically — never
   generate markup at runtime), the `is-step-N` / state CSS, effect
   keyframes copied from `shared/effects.css` (renamed to the abbr), and
   any `fg:step` handlers or custom interaction JS.
5. **Never edit inside `fg:begin <name> vN` / `fg:end <name>` sentinel
   blocks.** Those regions are owned by `scripts/build.js` and re-expanded
   from `shared/runtime/` and `shared/tokens.css`. Diagram-specific tuning
   uses the hook variables the blocks expose (`--fg-ctl-accent`,
   `--fg-cap-accent`, `--fg-cap-minh`) or additional rules outside the
   blocks.
6. Check: `node scripts/build.js --check && node scripts/validate.js`
   (also available as `npm run check`) — the validator enforces every hard
   rule below plus manifest sync.
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
| `palette-classic` / `palette-pastel-dark` / `palette-pastel-light` | scoped palette vars, derived from `shared/tokens.css` (local names: `--bg`, `--accent`, `--mint-fill`, …) — every palette also carries the shared type/shape/motion tokens (`--font`, `--mono`, `--radius`, `--radius-sm`, `--dur-step`, `--dur-fast`, `--ease`) |
| `palette-pastel-dark-prefixed` / `palette-pastel-light-prefixed` | same palettes with namespaced local names (`--pd-mint`, `--pl-mint-fill`) for files carrying more than one palette (effects-sampler) |
| `panel-base` / `panel-base-light` | panel background, radius, font, shadow, responsive `svg`/`text` base rules |
| `controls-bar` | prev/play/next/counter bar styling (`--fg-ctl-accent` overrides hover color) |
| `caption-box` | `.fg-caption` box (`--fg-cap-accent`, `--fg-cap-minh` overrides) |
| `reduced-motion` | kill-all transitions/animations under `prefers-reduced-motion` (extra reduced-motion rules go in a second `@media` outside the block) |
| `timeline-core` | `tl` step state machine (`is-step-N`, `fg:step` events, `is-playing`), control wiring, `reduced` flag — expects `TOTAL` and `STEP_MS` consts above it |
| `timeline-start` | initial `apply()` plus reduced-motion final-state jump or IntersectionObserver autoplay — place after any `fg:step` listeners |
| `hover-caption` | `data-info` → `.fg-caption` hover wiring |

`node scripts/build.js` re-expands every block (idempotent); `--check`
fails if any block drifted from its canonical source. Palette changes are
made in `shared/tokens.css`, then `node scripts/build.js` propagates them
to all 68+ diagrams. CI (`.github/workflows/validate.yml`) runs
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

- **Scoping.** Root element carries `fg-diagram fg-<diagram-name>`. Every CSS
  selector is prefixed with `.fg-<diagram-name>`. No bare element selectors,
  no styling `body`/`html`, no global keyframe names (prefix: `fg-<abbrev>-*`).
- **Namespaced ids.** SVG ids (markers, gradients, clips) are document-global
  once inlined — prefix them per diagram (e.g. `kvcf-arrowhead`). If the same
  diagram appears twice on a page, duplicate marker ids resolve to the first
  instance's definition; that's fine because definitions are identical.
- **Scoped JS.** One IIFE per diagram. Resolve the root via
  `document.currentScript.closest('.fg-diagram')` and query only within it.
  No globals, no `DOMContentLoaded` (the script sits after its markup), no
  `getElementById`.
- **Self-contained.** No external network requests: no webfonts, no CDN
  libraries, no linked CSS/JS inside the fragment. Copy what you need from
  `shared/`. `preview.css` may only be linked from `<head>` (outside the
  fragment).
- **No absolute paths** anywhere in the file.
- **Motion.** Ambient CSS animations are fine. Step timelines autoplay only
  when ~30% visible (IntersectionObserver) and pause off-screen. Under
  `prefers-reduced-motion`: kill transitions/animations and jump step
  timelines to the final state (manual controls stay usable).
- **Accessibility.** `role="img"` + meaningful `aria-label` on the SVG;
  `aria-label` on control buttons.
- **No layout shift.** Elements whose content changes at runtime (hover
  captions, step counters) must reserve their maximum height up front —
  size `min-height` for the longest text at column width — so interacting
  with a diagram never reflows the surrounding post.
- **Responsive.** SVG uses `viewBox` and `width: 100%; height: auto`. Design
  for a ~720px column; keep text ≥ 11px at natural size.

## Visual language

### Palettes

Three palettes live in `shared/tokens.css` (copy values, never link). Pick
per diagram:

- **Classic dark** (`--fg-*`, table below) — the default for dense
  technical diagrams (grids, matrices, pipelines).
- **Pastel-on-dark** (`--fg-pd-*`) — dark slate panel, soft pastel accents
  (mint `#a7f3d0`, lavender `#c4b5fd`, peach `#fed7aa`, rose `#fda4af`,
  baby-blue `#bae6fd`). Use for effect-heavy diagrams — glows and comets
  pop hardest on dark. Accents are contrast-safe as text and strokes.
- **Pastel-light** (`--fg-pl-*`) — cream panel (`#fdfbf7`/`#f6f1e7`) with
  pastel fill / saturated stroke / dark text TRIPLETS per accent. Gentler
  look for conceptual posts. Two hard rules: the panel MUST carry
  `border: 1px solid var(--fg-pl-border)` +
  `box-shadow: 0 2px 12px rgba(120,100,60,.10)` so it reads as a panel on
  the white blog page, and text on a pastel fill always uses that
  triplet's dark text color, never the muted ink.

The live reference for both pastel palettes (all swatches + every effect)
is `diagrams/effects-sampler/effects-sampler.html`.

### Effects catalog

`shared/effects.css` is the copy-source catalog of animation patterns:
**glow, highlight sweep, comet, draw-in, pulse/ripple, shimmer, flash** —
each with markup, technique, and reduced-motion fallback. Rename the
`fg-XX-*` keyframe placeholders to the diagram's abbreviation when
copying. Additional hard rules that come with the effects:

- **Never animate SVG filter primitives.** Filters re-render per frame
  and jank. Blur a duplicate node once, statically; animate only its
  opacity (this is the glow pattern).
- **SMIL ignores `prefers-reduced-motion`.** Every `<animateMotion>`
  comet group must be gated off with CSS `display: none` under the
  reduced-motion media query — the CSS gate is mandatory, not optional.
- **Taste:** one hero effect per step, at most ~3 animated elements
  concurrently. Effects must explain (a comet shows direction, a glow
  shows activation, a ripple shows an in-place update) — decoration for
  its own sake reads as noise on a technical blog.

Step-triggered one-shots use `restartAnimation()` and `launchComets()`
from `shared/snippets.js` (comets authored with `begin="indefinite"`,
kicked from the `fg:step` handler; trails chain off the head via
syncbase timing, e.g. `begin="xx-head.begin+0.1s"`).

### Classic dark tokens

Dark slate panel on the blog's light page (matches its mermaid diagrams):

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

Easing and step transitions always come from the palette block: `var(--ease)`
and `var(--dur-fast)` (0.45s state transitions) / `var(--dur-step)` (700ms
timeline cadence). The validator rejects literal `cubic-bezier()` or
hand-mixed dim hexes outside managed blocks.

Font: `"Work Sans", system-ui, -apple-system, "Segoe UI", sans-serif`
(system fallback — never fetch webfonts). Rounded corners (12px panel,
6px blocks), 700ms step transitions, `cubic-bezier(0.4, 0, 0.2, 1)`.

Interaction patterns to reuse (see `shared/snippets.js`):
- **Step timeline** — root class `is-step-N` drives CSS states; prev/play/next
  controls; good for loops, cache fills, pipelines.
- **Hover-to-inspect** — blocks carry `data-info`; a `.fg-caption` box below
  the SVG shows details; good for architecture block diagrams.
- **Ambient flow** — dashed `stroke-dasharray` lines with a `stroke-dashoffset`
  keyframe animation for data flowing along paths.

## Embedding in the blog

The blog repo mounts this repo as a git submodule at `static/diagrams` and
provides a shortcode:

```
{{</* diagram name="inference-loop/kv-cache-fill" caption="..." */>}}
```

After changing diagrams here, bump the submodule in the blog repo:
`git submodule update --remote static/diagrams && git add static/diagrams`
and commit.
