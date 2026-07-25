# Authoring guide — visual language

The mechanical rules are in [CLAUDE.md](../CLAUDE.md) and enforced by
the validator; this doc is about making a diagram that looks and
behaves like the rest of the library. The live reference for every
swatch and effect is `diagrams/effects-sampler/effects-sampler.html`.

## Choosing a kind

| kind | when | interaction |
|---|---|---|
| **step-timeline** | a process unfolds over discrete steps: loops, cache fills, pipelines | prev/play/next controls drive `is-step-N` root classes; autoplays when ~30% visible, pauses off-screen |
| **hover-inspect** | an architecture/block diagram where parts need explanation | blocks carry `data-info`; hovering fills the `.fg-caption` box |
| **ambient** | continuous flow with no natural steps | looping CSS animation (e.g. dashed-line `stroke-dashoffset` flow) |
| **hero** | a cinematic wide-aspect post hero — abstract art inspired by the post, sets a mood rather than explains | no controls; intro choreography fires once at ~30% visibility (`is-live`), settles after `INTRO_MS` (`is-settled`), then a quiet ambient loop that pauses off-screen (`is-paused`) |

Kinds compose — a step timeline can also have hover captions — but
start from the template closest to the primary interaction.

## Hero raster style

Heroes deliberately break from the crisp vector look of the other
kinds: they read as frames of an encoded GIF while staying live SVG.
The recipe (copy-sources in the RASTER KIT section of
`shared/effects.css`; live reference in the effects sampler):

- **Pixel grid** — 4 viewBox units = 1 raster "pixel" (a 1200×500 hero
  is a 300×125 pixel canvas). Snap every coordinate, set
  `shape-rendering: crispEdges` on the `<svg>`, and drop all `rx`
  rounding.
- **Frame-quantized motion** — entrances use `var(--ease-frames)` or
  `var(--ease-frames-coarse)`; ambient loops tick as
  `calc(var(--dur-tick) * N)` with a matching `steps(N)`. Nothing
  glides; everything jumps between frames.
- **Posterized texture** — Bayer dither patterns instead of gradients,
  a scanline overlay, static `feTurbulence` grain (never animate
  filter primitives), dithered blink halos instead of blur glows, and
  staircase paths instead of smooth beziers.
- **Abstract, not labeled** — heroes evoke the post's subject without
  diagram anatomy: no axis labels, no captions inside the art.
- `image-rendering: pixelated` does nothing for SVG shapes — don't
  cargo-cult it; the chunkiness comes from the grid and `crispEdges`.

The v2 tier of the kit (same section of `shared/effects.css`, live in
the sampler's bottom row):

- **Discrete posterize** — `feComponentTransfer type="discrete"` snaps
  gradients into hard indexed-color bands;
  `color-interpolation-filters="sRGB"` is mandatory or the bands land
  wrong. Filters go on **static** subtrees only — a filter over
  animating content re-rasterizes every frame.
- **RGB split** — red/cyan duplicates offset ±1 raster pixel with
  `mix-blend-mode: screen` inside an `isolation: isolate` group; the
  stepped jitter variant is intro-only.
- **Checkerboard dissolve** — elements enter by hard-cutting through
  dither densities (25 → 50 → 75 → solid) with `steps(1)`. **No plain
  opacity fades in heroes** — smooth alpha is the biggest "modern web"
  tell in a retro frame.
- **Band glitch** — group copies clipped to horizontal bands, shearing
  via held-frame stepped transforms. Transform only, never animate the
  clip-path; gated off under reduced motion.
- **Interlace flicker** — two offset scanline layers alternating with
  `steps(2)`. Hard limits: opacity delta ≤ 0.1, cycle ≥
  `var(--dur-flicker)` (800ms) — WCAG 2.3.1; reduced-motion gated.
- **Static pixelation** — the feFlood→feTile→feMorphology chain
  pixelates content you can't hand-grid (text, gradient blobs); static
  subtrees only, explicit filter region for Safari.
- Perf: SVG `<pattern>` fills over large areas are a Chromium slow
  path — full-panel dither is cheaper as a CSS
  `repeating-conic-gradient` background on the container.

### Clean pixel-art sprites (the alternative hero style)

Figurative heroes can skip the raster kit entirely and be drawn as
hand-placed pixel sprites — plain `<rect>`s on a coarse cell grid
(8 viewBox units per cell reads well at column width), animated only
with `steps()` flipbook keyframes. The craft rules that make sprites
read as art rather than programmer boxes:

- **Sprite ramps, not flat fills** — every material gets 3–4 shades
  from the `--px-*` ramp tokens in `shared/tokens.css`, hue-shifted:
  shadows lean cool (blue-violet), highlights lean warm. One
  consistent light source (top-left) across the whole scene.
- **Selective outlines** — silhouettes carry a `--px-outline`
  (dark blue-violet, not black) edge; interior detail uses the
  ramp's shadow shade instead.
- **Grounding** — contact shadows under everything that touches the
  floor, and set dressing (shelf, poster, floor dither) so the scene
  reads as a place, not sprites on a void.
- **Animation principles at low frame counts** — anticipation before
  an action, a frame of overshoot after it, 2–4-frame sprite-swap
  flipbooks (discrete opacity groups on one `steps(1, jump-end)`
  master timeline) instead of tweens.

Reference implementation: `diagrams/linux-ai-setup/robot-boot-hero.html`
(generated from ASCII pixel maps; horizontal same-color runs merged
into single rects).

Watchlist (documented, deliberately not kit yet): scroll-driven
`animation-timeline` + steps() flipbooks (Firefox stable still
flagged), feImage/feDisplacementMap CRT warp (Safari feImage
flakiness; animating it would break the static-filter rule).

## Palette semantics

One palette, classic dark, defined in `shared/tokens.css` and stamped
in via the `palette-classic` block (full value table in
[CLAUDE.md](../CLAUDE.md#classic-dark-tokens)). The hues carry
meaning; use them consistently so readers can transfer intuition
between diagrams:

- `--accent` (sky) — the thing currently happening: active flow,
  highlights, the hot element of the current step.
- `--ok` (green) — settled state: filled, cached, residual, done.
- `--warn` (amber) — in progress or the hot path: decode, work in
  flight.
- `--hot` (red) — trouble: bottleneck, eviction, contention.
- `--violet` — a second series when one hue isn't enough.
- `--*-dim` variants — the *fill* of a box that is active in the
  current step (accent hue ~15% over panel). Always the token, never a
  hand-mixed hex — the validator rejects the known hand-mixed values.

Typography and shape come with the blocks: system font stack (never
fetch webfonts), 12px panel radius, 6px block radius, `var(--ease)`
easing, `var(--dur-fast)` (0.45s) state transitions, `var(--dur-step)`
(700ms) timeline cadence.

## Effects

`shared/effects.css` is a copy-source catalog — copy the pattern into
your fragment and rename the `fg-XX-*` keyframes to your abbr:

- **glow** — activation: a statically-blurred duplicate node whose
  opacity animates.
- **highlight sweep** — attention passing over a region.
- **comet** — directional data movement along a path (SMIL
  `<animateMotion>`, kicked from a `fg:step` handler via
  `launchComets()`; trails chain off the head with syncbase timing).
- **draw-in** — a connection being established (stroke-dash reveal).
- **pulse/ripple** — an in-place update.
- **shimmer** — pending/loading state.
- **flash** — a discrete event.

Two hard rules travel with the effects (both are contract rules, both
checked in review even where the validator can't see them):

1. **Never animate SVG filter primitives** — filters re-render per
   frame and jank. Blur once statically, animate opacity only.
2. **CSS-gate every SMIL animation** with `display: none` under
   `prefers-reduced-motion`, because SMIL ignores the media query on
   its own. The validator enforces this for `<animateMotion>`.

### Taste

- One hero effect per step; at most ~3 elements animating at once.
- Every effect must explain something — a comet shows direction, a
  glow shows activation, a ripple shows an in-place update. Decoration
  for its own sake reads as noise on a technical blog.
- Design for a ~720px column; keep text ≥ 11px at natural SVG size.

## Accessibility and motion

- `role="img"` and a meaningful `aria-label` on the SVG; `aria-label`
  on every control button.
- Under `prefers-reduced-motion`: all transitions/animations killed
  (the `reduced-motion` managed block does the blanket kill; add extra
  rules in a second `@media` outside the block), step timelines jump
  to the final state, and manual controls stay usable.
- **No layout shift**: anything whose content changes at runtime
  (hover captions, step counters) reserves its maximum height up front
  — size `min-height` for the longest text at column width. The
  `--fg-cap-minh` hook exists for exactly this.

## Workflow reminders

- Read 1–2 existing diagrams of the same kind before writing one.
- Scaffold with `scripts/new-diagram.js`
  ([development.md](development.md#creating-a-diagram)), fill in the
  manifest `description`, and finish with `npm run check` plus a
  gallery look.
