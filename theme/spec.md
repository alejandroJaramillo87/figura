# Slide authoring spec (Level 1)

Rules for authoring a Slidegen slide. Written for LLM or human authors.
`slidegen validate` enforces most of these mechanically; write to pass it
on the first try.

## File shape

- One HTML file in `slides/`, named `NN-name.html` (e.g. `01-intro.html`).
- Link the theme via relative path: `<link rel="stylesheet" href="../theme/theme.css">`.
- Root element: `<div class="slide" data-loop-ms="6000">…</div>`.
  `.slide` fixes the canvas at 1600×900 — do not override its size.
- No JavaScript. No network resources (`http://`/`https://` anywhere fails
  validate). Fonts: system stack from the theme, or local `@font-face` with a
  relative url.

## Color

Use theme variables only (`var(--accent)`, `var(--ink)`, …). Any hex, `rgb()`,
or `hsl()` literal in the slide file fails validate. Need a new color? Add a
token to `theme/theme.css` instead.

## Animation rules

- **CSS animations only. CSS transitions are banned** (the renderer freezes
  and scrubs animations; transitions are neither frozen nor scrubbed and will
  render wrong). Validate rejects any `transition` property.
- The slide loops every `data-loop-ms` milliseconds. For every animation:
  `delay + duration × iteration-count` must be ≤ `data-loop-ms`. Infinite
  iteration counts are not allowed. Validate reads the live animations and
  hard-fails violations.
- `data-loop-ms` must be divisible by the frame interval (default 70 ms).
  Valid values: multiples of 70 — e.g. 4200, 5600, 6300, 7000.
- **Seamless loop**: the slide must look identical at t=0 and t=loop
  (validate compares them with SSIM ≥ 0.995). Practical recipe: elements
  start hidden (`opacity: 0`), animate in with
  `animation-fill-mode: forwards`, and… they now end visible while t=0 has
  them hidden — that breaks the seam. Two sanctioned patterns:
  1. **Fade the whole slide's transient elements back out** before the loop
     ends (an exit animation completing before `loop-ms`), or
  2. Make the resting state the *animated-to* state at both ends: give the
     element a final segment that returns it to its t=0 appearance.
- **Quiet final 500 ms**: nothing moves in the last 500 ms of the loop. All
  animations finish by `data-loop-ms − 500`. This gives the loop a moment of
  rest and hides encoder artifacts at the seam.

## Fill modes, briefly

- `animation-fill-mode: forwards` keeps the final keyframe after the
  animation ends — use it for enter animations, but remember the seam rule.
- `backwards` applies the first keyframe during the delay — use it so
  delayed elements don't flash their resting style before starting.
- `both` = both of the above; the usual right answer for enter animations.

## Shared utilities

`theme.css` ships `anim-fade-in`, `anim-rise-in`, and `anim-sweep-underline`.
Override `animation-delay`/`animation-duration` inline in your slide's
`<style>` block to stagger them. Custom `@keyframes` in the slide are fine at
Level 1 — follow the loop rules above.
