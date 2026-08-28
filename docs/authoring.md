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

Kinds compose — a step timeline can also have hover captions — but
start from the template closest to the primary interaction.

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
fetch webfonts), 12px panel radius, `var(--ease)` easing and
`var(--dur-fast)` (0.45s) state transitions. Timeline cadence is per
diagram, set by the `STEP_MS` const above the `timeline-core` block.

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

- One lead effect per step; at most ~3 elements animating at once.
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
