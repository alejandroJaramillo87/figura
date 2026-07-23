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
3. Copy needed palette values from `shared/tokens.css` and helper patterns
   from `shared/snippets.js` into the new file (copy, never link — see below).
4. Create `diagrams/<post-slug>/<kebab-name>.html` where `<post-slug>`
   matches the blog post's filename stem in `content/posts/`.
5. Append an entry to `manifest.json` (`id`, `path`, `title`, `post`,
   `description`).
6. Preview: open the file directly in a browser, and check the gallery
   (`python3 -m http.server`, open `index.html`) — the gallery renders the
   first manifest entry twice as a multi-instance regression check.

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

<!-- sa:embed-start -->
<div class="sa-diagram sa-<diagram-name>">
  <style>/* everything scoped under .sa-<diagram-name> */</style>
  <svg viewBox="0 0 W H" role="img" aria-label="...">…</svg>
  <!-- optional: .sa-caption box, .sa-controls bar -->
  <script>(() => {
    const root = document.currentScript.closest('.sa-diagram');
    /* query only within root */
  })();</script>
</div>
<!-- sa:embed-end -->
</body>
</html>
```

Only the fragment between `<!-- sa:embed-start -->` and `<!-- sa:embed-end -->`
is inlined into the blog. Everything the diagram needs must live inside it.

## Hard rules (the blog inlines this fragment into a busy page)

- **Scoping.** Root element carries `sa-diagram sa-<diagram-name>`. Every CSS
  selector is prefixed with `.sa-<diagram-name>`. No bare element selectors,
  no styling `body`/`html`, no global keyframe names (prefix: `sa-<abbrev>-*`).
- **Namespaced ids.** SVG ids (markers, gradients, clips) are document-global
  once inlined — prefix them per diagram (e.g. `kvcf-arrowhead`). If the same
  diagram appears twice on a page, duplicate marker ids resolve to the first
  instance's definition; that's fine because definitions are identical.
- **Scoped JS.** One IIFE per diagram. Resolve the root via
  `document.currentScript.closest('.sa-diagram')` and query only within it.
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

- **Classic dark** (`--sa-*`, table below) — the default for dense
  technical diagrams (grids, matrices, pipelines).
- **Pastel-on-dark** (`--sa-pd-*`) — dark slate panel, soft pastel accents
  (mint `#a7f3d0`, lavender `#c4b5fd`, peach `#fed7aa`, rose `#fda4af`,
  baby-blue `#bae6fd`). Use for effect-heavy diagrams — glows and comets
  pop hardest on dark. Accents are contrast-safe as text and strokes.
- **Pastel-light** (`--sa-pl-*`) — cream panel (`#fdfbf7`/`#f6f1e7`) with
  pastel fill / saturated stroke / dark text TRIPLETS per accent. Gentler
  look for conceptual posts. Two hard rules: the panel MUST carry
  `border: 1px solid var(--sa-pl-border)` +
  `box-shadow: 0 2px 12px rgba(120,100,60,.10)` so it reads as a panel on
  the white blog page, and text on a pastel fill always uses that
  triplet's dark text color, never the muted ink.

The live reference for both pastel palettes (all swatches + every effect)
is `diagrams/effects-sampler/effects-sampler.html`.

### Effects catalog

`shared/effects.css` is the copy-source catalog of animation patterns:
**glow, highlight sweep, comet, draw-in, pulse/ripple, shimmer, flash** —
each with markup, technique, and reduced-motion fallback. Rename the
`sa-XX-*` keyframe placeholders to the diagram's abbreviation when
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
kicked from the `sa:step` handler; trails chain off the head via
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
| `--line` | `#64748b` | connectors, arrowheads |

Font: `"Work Sans", system-ui, -apple-system, "Segoe UI", sans-serif`
(system fallback — never fetch webfonts). Rounded corners (12px panel,
6px blocks), 700ms step transitions, `cubic-bezier(0.4, 0, 0.2, 1)`.

Interaction patterns to reuse (see `shared/snippets.js`):
- **Step timeline** — root class `is-step-N` drives CSS states; prev/play/next
  controls; good for loops, cache fills, pipelines.
- **Hover-to-inspect** — blocks carry `data-info`; a `.sa-caption` box below
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
