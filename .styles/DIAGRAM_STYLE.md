# Diagram style guide

The contract every diagram, template and shared runtime file in this repository follows: how a
diagram is made, what its fragment may contain, and which check holds each rule. The blog
inlines each fragment verbatim into a busy page, so a rule broken here breaks a published post.

Each hard rule ends with the validator rule ids that enforce it (`scripts/validate.js`), the
browser check that does (`tests/render.test.mjs`), or "Checked in review" when nothing
mechanical can. `tests/check-contract.mjs` fails when a validator rule goes uncited here or this
guide cites one that does not exist, so the tags stay honest. The existing diagrams under
`diagrams/` are the style reference: read one or two of the same kind before writing a new one.

## Table of Contents

<!-- toc:start -->

1. [Workflow for a new diagram](#workflow-for-a-new-diagram)
2. [Managed blocks](#managed-blocks)
3. [File anatomy](#file-anatomy)
4. [Hard rules](#hard-rules)
5. [Effects](#effects)
6. [Tokens](#tokens)
7. [Interaction patterns](#interaction-patterns)

<!-- toc:end -->

## Workflow for a new diagram

1. Read the diagram notes provided by the author.
2. Read one or two existing diagrams closest in kind: `step-timeline`, `hover-inspect`,
   `toggle`, `ambient` or `static`.
3. Scaffold the file. This also appends the `manifest.json` entry, whose `description` you
   fill in:

   ```bash
   node scripts/new-diagram.js <consumer-dir>/<kebab-name> \
     --kind step-timeline|hover-inspect|toggle|ambient|static \
     --abbr <2-6 char prefix> --title "Human-readable title"
   ```

   `<consumer-dir>` names where the diagram is used: the blog post's filename stem, the series
   directory for a post in a series (`what-language-leaves-out/`), or the docs-site section for
   a static diagram (`rust-harness/`). Once a page embeds or copies the diagram, add it to the
   entry's `consumers` list as `<repo>:<path>`.
4. Author only the diagram-specific parts: the SVG, written statically and never generated at
   runtime; the `is-step-N` or state CSS; the `STATES` or `CAPTIONS` table a toggle or captioned
   timeline reads; effect keyframes copied from `shared/effects.css` and renamed to the
   abbreviation; and any `fg:step`, `fg:toggle` or `fg:hover` handlers.
5. Run `npm run check` while authoring, and `npm run quality` before pushing.
6. Preview the file in a browser, and the gallery (`python3 -m http.server`, then open
   `index.html`), which renders the first manifest entry twice as a multi-instance check.
   `npm run quality:full` repeats both in a headless browser.

Leftover scaffold placeholders and a manifest entry out of step with its file fail the gate.
Checked by: `scaffold`, `title`, `manifest`, `manifest-id`.

## Managed blocks

Boilerplate every diagram needs is not hand-copied. It lives once under `shared/runtime/` (and,
for the palette, in `shared/tokens.css`) and is stamped into each fragment between sentinel
comments: `/* fg:begin controls-bar v1 */ ... /* fg:end controls-bar */` in CSS, and
`// fg:begin timeline-core v1 ... // fg:end timeline-core` in JS.

**Never edit inside a sentinel block.** `scripts/build.js` owns those regions and rewrites
them from their source. Tune a diagram with the hook variables a block exposes
(`--fg-ctl-accent`, `--fg-cap-accent`, `--fg-cap-minh`) or with rules outside the block, and
change a block itself in its source file, then run `npm run build`. `build --check` fails a
drifted block. Checked by: `sentinel`, `block-unknown`, `block-version`.

<!-- inventory:blocks:start -->

| Block | Provides |
|-------|----------|
| `palette-classic` | Scoped palette variables derived from `shared/tokens.css` (local names such as `--bg`, `--accent` and `--ok-dim`), the shared type, shape and motion tokens, and zero-specificity `fg-fill-<token>` and `fg-stroke-<token>` classes that stand in for colour attributes. |
| `panel-base` | Panel background, radius, font and shadow, and the responsive `svg` and `text` base rules. |
| `reduced-motion` | Stops every transition and animation under `prefers-reduced-motion`; extra reduced-motion rules go in a second `@media` outside the block. |
| `controls-bar` | Prev, play, next and counter bar styling; `--fg-ctl-accent` overrides the hover colour. |
| `timeline-core` | The `tl` step state machine (`is-step-N`, `fg:step` events, `is-playing`), control wiring and the `reduced` flag; expects `TOTAL` and `STEP_MS` constants above it. |
| `timeline-start` | The initial `apply()`, then the reduced-motion jump to the final step, or autoplay once 30% visible that a reader's pause turns off; place it after any `fg:step` listeners. |
| `caption-box` | The `.fg-caption` box (`--fg-cap-accent` and `--fg-cap-minh` hooks), the grid that reserves the tallest caption's height, and the focus ring for `data-info` targets. |
| `caption-core` | `reserveCaption(variants)` and `setCaption(html)`, which stack every caption variant invisibly so the box never changes height, and announce changes through `aria-live`. |
| `hover-caption` | Shows a `data-info` target's readout (with optional `data-title` and `data-code`) on hover and on keyboard focus, and emits `fg:hover` with `{ el, index, on }`. |
| `step-caption` | Renders `CAPTIONS[step]` (text, or `[title, text]`) into the caption on each `fg:step`. |
| `toggle-bar` | Toggle button bar styling, pressed state and focus ring. |
| `toggle-core` | A `STATES` table (`{ cls, cap, label? }`) driven by one cycling `data-fg="toggle"` button or one button per state, with `tg.show(n)`, `tg.next()` and `fg:toggle` events. |
| `instance-ids` | In the second and later copies of a diagram on one page, suffixes ids and rewrites `href`, `url(#...)` and SMIL syncbase references; required wherever syncbase timing appears. |

<!-- inventory:blocks:end -->

Each manifest `kind` requires a set of blocks, in dependency order. Every kind carries
`palette-classic`, `panel-base` and `reduced-motion`. `step-timeline` adds `controls-bar`,
`timeline-core` and `timeline-start`; `hover-inspect` adds `caption-box`, `caption-core` and
`hover-caption`; `toggle` adds `toggle-bar`, `caption-box`, `caption-core` and `toggle-core`.
A block's version (`v1`) is its interface version: it changes only when what the host diagram
must provide changes, and a stale version fails. Checked by: `block-required`, `block-order`,
`block-duplicate`.

## File anatomy

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Human-readable diagram title</title>
<link rel="stylesheet" href="../../shared/preview.css">
</head>
<body>
<h1>Human-readable diagram title</h1>
<p>One-line description for standalone viewing.</p>

<!-- fg:embed-start -->
<div class="fg-diagram fg-<diagram-name>">
  <style>/* everything scoped under .fg-<diagram-name> */</style>
  <svg viewBox="0 0 W H" role="img" aria-label="...">...</svg>
  <script>(() => {
    const root = document.currentScript.closest('.fg-diagram');
  })();</script>
</div>
<!-- fg:embed-end -->
</body>
</html>
```

Only the fragment between the two embed markers is inlined into the blog, so everything the
diagram needs lives inside it. An optional `.fg-caption` box and `.fg-controls` bar sit after
the SVG. `preview.css` is page chrome for standalone viewing and is linked only from `<head>`.
Checked by: `embed-markers`.

## Hard rules

- **Scoping.** The root element carries `fg-diagram fg-<diagram-name>`, where
  `<diagram-name>` is the file stem. Every CSS selector, including inside `@media`,
  `@supports`, `@container` and `@layer`, starts with `.fg-<diagram-name>`: no bare element
  selectors, and no styling of `body` or `html`. Keyframe names carry the `fg-<abbr>-` prefix.
  Checked by: `root-class`, `css-scope`, `keyframes`.
- **Namespaced ids.** SVG ids (markers, gradients, clips) are document-global once inlined, so
  each carries the diagram's prefix (`kvcf-arrowhead`), and no id or keyframe name repeats one
  another diagram defines. Every `url(#id)` and `href="#id"` names an id the fragment defines.
  Two copies of one diagram on a page share identical marker definitions harmlessly, but not
  SMIL syncbase timing, which the `instance-ids` block rewrites.
  Checked by: `id-prefix`, `global-name`, `id-ref`, `instance-ids`.
- **No HTML comments** inside the fragment: the blog inlines it verbatim, so they ship to
  readers. Explain markup in the `<style>` or in the commit. Checked by: `html-comment`.
- **Tokens only.** No literal colours outside managed blocks: CSS uses the palette variables,
  and an SVG colour attribute becomes an `fg-fill-*` or `fg-stroke-*` class. Active fills use
  the `--*-dim` tokens, never a hand-mixed hex. Easing is `var(--ease)`; transition durations
  are `var(--dur-quick)`, `var(--dur-fast)` or `var(--dur-slow)`; monospace text uses
  `var(--mono)`. Checked by: `color-token`, `dim-token`, `motion-token`, `font-token`.
- **Scoped JS.** One bare `<script>` holding exactly one IIFE that parses. It resolves its root
  with `document.currentScript.closest('.fg-diagram')` and queries only within it. No globals,
  no `DOMContentLoaded` (the script sits after its markup), and no `getElementById`.
  Checked by: `js-scope`, `js-syntax`.
- **Self-contained.** No external network requests: no webfonts, no CDN libraries, no linked
  CSS or JS, no `@import`, and no relative URLs, which would resolve against the blog page.
  Copy what the diagram needs from `shared/`. Checked by: `self-contained`.
- **No absolute paths** anywhere in the file. Checked by: `absolute-path`.
- **Motion.** Ambient CSS animation is fine. A step timeline autoplays only when about 30%
  visible and pauses off-screen, which `timeline-start` provides. Under
  `prefers-reduced-motion`, transitions and animations stop and a step timeline shows its
  final step, with manual controls still usable. Checked by: `reduced-motion`,
  `block-required`, and `tests/render.test.mjs` for the final step.
- **Accessibility.** The SVG carries `role="img"` and an `aria-label` that says what the
  diagram shows. Control buttons carry `type="button"` and an `aria-label`. Nothing inside the
  `role="img"` SVG takes `role="button"`, because assistive technology cannot reach it:
  interactive state is driven by real buttons in `.fg-controls`, and hover readouts are reached
  by keyboard focus through `hover-caption`. Checked by: `a11y` for the SVG attributes; the
  label's meaning and the buttons are checked in review.
- **No layout shift.** Anything whose content changes at runtime reserves its largest height
  up front, so driving a diagram never reflows the post around it. Captions do this through
  `caption-core`; anything else sizes its own `min-height`. Checked by
  `tests/render.test.mjs`, at 760px and 360px.
- **Responsive.** The SVG uses a `viewBox` with `width: 100%; height: auto`, designed for a
  column of about 720px. Text is at least 11px at natural size. Checked by: `font-size`; the
  viewBox sizing is checked in review.
- **Static kind.** A diagram whose manifest entry says `"kind": "static"` carries no
  `<script>`, no SMIL element, no `@keyframes`, no `animation` or `transition` outside the
  managed blocks, and no `.fg-controls` or `.fg-caption` markup. It encodes state with palette
  hues, not motion, because it exists for consumers that cannot inline HTML or run script:
  `npm run export` writes it to `exports/<slug>/<name>.svg` as a standalone image.
  Checked by: `static-script`, `static-smil`, `static-motion`, `static-chrome`, and
  `export --check` for the committed image.

## Effects

`shared/effects.css` is the copy-source catalog of animation patterns (glow, highlight sweep,
comet, draw-in, pulse and ripple, shimmer, flash), each with markup, technique and a
reduced-motion fallback. Rename its `fg-XX-*` keyframe placeholders to the diagram's
abbreviation when copying. Step-triggered one-shots use `restartAnimation()` and
`launchComets()` from `shared/snippets.js`: comets are authored with `begin="indefinite"` and
started from the `fg:step` handler, and trails chain off the head through syncbase timing
(`begin="xx-head.begin+0.1s"`), which requires the `instance-ids` block.

- **Never animate SVG filter primitives.** A filter re-renders every frame. Blur a duplicate
  node once, statically, and animate only its opacity; that is the glow pattern. Checked in
  review.
- **Gate every SMIL element.** SMIL ignores `prefers-reduced-motion`, so each `animate`,
  `animateMotion`, `animateTransform` and `set` sits inside an element hidden with CSS
  `display: none` under the reduced-motion media query. Checked by: `smil-gate`.
- **One lead effect per step**, and at most about three animated elements at once. An effect
  explains something: a comet shows direction, a glow shows activation, a ripple shows an
  in-place update. Checked in review.

## Tokens

One palette, classic dark, lives in `shared/tokens.css` and reaches every diagram through the
`palette-classic` block; a diagram never links it. The dark slate panel reads as a framed figure
on the blog's light theme and sits nearly flush on the dark one, so diagrams never switch
theme. The live reference for every swatch and effect is
`diagrams/effects-sampler/effects-sampler.html`.

<!-- inventory:tokens:start -->

| Token | Value | Use |
|-------|-------|-----|
| `--bg` | `#0f172a` | panel background |
| `--panel` | `#1e293b` | blocks, cells |
| `--panel-hover` | `#334155` | hover fill |
| `--border` | `#334155` | strokes |
| `--text` | `#f8fafc` | primary labels |
| `--muted` | `#94a3b8` | secondary labels |
| `--accent` | `#38bdf8` | highlights, active flow lines |
| `--ok` | `#34d399` | filled, cached, residual |
| `--warn` | `#fbbf24` | in progress, decode, hot path |
| `--hot` | `#f87171` | bottleneck, eviction, error |
| `--violet` | `#a78bfa` | secondary series (K against V, a second head) |
| `--accent-dim` | `#0c3550` | active box fill for accent |
| `--ok-dim` | `#0e4429` | active box fill for ok |
| `--warn-dim` | `#4a3608` | active box fill for warn |
| `--hot-dim` | `#4a1d1d` | active box fill for hot |
| `--violet-dim` | `#2a2350` | active box fill for violet |
| `--line` | `#64748b` | connectors, arrowheads |
| `--font` | `"Work Sans", system-ui, -apple-system, "Segoe UI", sans-serif` | all text |
| `--mono` | `ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace` | code, numbers |
| `--radius` | `12px` | panel corners |
| `--dur-quick` | `0.3s` | hover and focus feedback |
| `--dur-fast` | `0.45s` | state transitions |
| `--dur-slow` | `0.7s` | draw-in and step cadence effects |
| `--ease` | `cubic-bezier(0.4, 0, 0.2, 1)` | every transition |

<!-- inventory:tokens:end -->

Timeline cadence is set per diagram by the `STEP_MS` constant the `timeline-core` block reads.
The font is `"Work Sans"` with a system fallback, never a fetched webfont.

## Interaction patterns

One pattern per kind:

- **Step timeline.** The root class `is-step-N` drives CSS states, with prev, play and next
  controls. Suits loops, cache fills and pipelines.
- **Hover to inspect.** Blocks carry `data-info`, and the `.fg-caption` box below the SVG shows
  the details. Suits architecture block diagrams.
- **Toggle.** A button flips or cycles the root through `STATES`, each with its caption. Suits
  two readings of one sentence.
- **Ambient flow.** Dashed `stroke-dasharray` lines with a `stroke-dashoffset` keyframe show
  data moving along paths.
- **Static.** No motion and no script; see the static rule above.
