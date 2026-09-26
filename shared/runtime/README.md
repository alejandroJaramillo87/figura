# Runtime blocks

The canonical source of every managed block that `scripts/build.js` stamps into diagrams between
`fg:begin` and `fg:end` sentinels.

A block file is stamped verbatim, so it carries no header comment; its description lives here,
in a describe line the generator reads. The same lines render the block table in
`.styles/DIAGRAM_STYLE.md`. `palette-classic` has no file here: `scripts/lib/fragment.js`
generates it from `shared/tokens.css`.

<!-- describe palette-classic: Scoped palette variables derived from `shared/tokens.css` (local names such as `--bg`, `--accent` and `--ok-dim`), the shared type, shape and motion tokens, and zero-specificity `fg-fill-<token>` and `fg-stroke-<token>` classes that stand in for colour attributes. -->
<!-- describe panel-base.css: Panel background, radius, font and shadow, and the responsive `svg` and `text` base rules. -->
<!-- describe reduced-motion.css: Stops every transition and animation under `prefers-reduced-motion`; extra reduced-motion rules go in a second `@media` outside the block. -->
<!-- describe controls-bar.css: Prev, play, next and counter bar styling; `--fg-ctl-accent` overrides the hover colour. -->
<!-- describe timeline-core.js: The `tl` step state machine (`is-step-N`, `fg:step` events, `is-playing`), control wiring and the `reduced` flag; expects `TOTAL` and `STEP_MS` constants above it. -->
<!-- describe timeline-start.js: The initial `apply()`, then the reduced-motion jump to the final step, or autoplay once 30% visible that a reader's pause turns off; place it after any `fg:step` listeners. -->
<!-- describe caption-box.css: The `.fg-caption` box (`--fg-cap-accent` and `--fg-cap-minh` hooks), the grid that reserves the tallest caption's height, and the focus ring for `data-info` targets. -->
<!-- describe caption-core.js: `reserveCaption(variants)` and `setCaption(html)`, which stack every caption variant invisibly so the box never changes height, and announce changes through `aria-live`. -->
<!-- describe hover-caption.js: Shows a `data-info` target's readout (with optional `data-title` and `data-code`) on hover and on keyboard focus, and emits `fg:hover` with `{ el, index, on }`. -->
<!-- describe step-caption.js: Renders `CAPTIONS[step]` (text, or `[title, text]`) into the caption on each `fg:step`. -->
<!-- describe toggle-bar.css: Toggle button bar styling, pressed state and focus ring. -->
<!-- describe toggle-core.js: A `STATES` table (`{ cls, cap, label? }`) driven by one cycling `data-fg="toggle"` button or one button per state, with `tg.show(n)`, `tg.next()` and `fg:toggle` events. -->
<!-- describe instance-ids.js: In the second and later copies of a diagram on one page, suffixes ids and rewrites `href`, `url(#...)` and SMIL syncbase references; required wherever syncbase timing appears. -->

<!-- inventory:pages:start -->

| File | Holds |
|------|-------|
| [caption-box.css](caption-box.css) | The `.fg-caption` box (`--fg-cap-accent` and `--fg-cap-minh` hooks), the grid that reserves the tallest caption's height, and the focus ring for `data-info` targets. |
| [caption-core.js](caption-core.js) | `reserveCaption(variants)` and `setCaption(html)`, which stack every caption variant invisibly so the box never changes height, and announce changes through `aria-live`. |
| [controls-bar.css](controls-bar.css) | Prev, play, next and counter bar styling; `--fg-ctl-accent` overrides the hover colour. |
| [hover-caption.js](hover-caption.js) | Shows a `data-info` target's readout (with optional `data-title` and `data-code`) on hover and on keyboard focus, and emits `fg:hover` with `{ el, index, on }`. |
| [instance-ids.js](instance-ids.js) | In the second and later copies of a diagram on one page, suffixes ids and rewrites `href`, `url(#...)` and SMIL syncbase references; required wherever syncbase timing appears. |
| [panel-base.css](panel-base.css) | Panel background, radius, font and shadow, and the responsive `svg` and `text` base rules. |
| [reduced-motion.css](reduced-motion.css) | Stops every transition and animation under `prefers-reduced-motion`; extra reduced-motion rules go in a second `@media` outside the block. |
| [step-caption.js](step-caption.js) | Renders `CAPTIONS[step]` (text, or `[title, text]`) into the caption on each `fg:step`. |
| [timeline-core.js](timeline-core.js) | The `tl` step state machine (`is-step-N`, `fg:step` events, `is-playing`), control wiring and the `reduced` flag; expects `TOTAL` and `STEP_MS` constants above it. |
| [timeline-start.js](timeline-start.js) | The initial `apply()`, then the reduced-motion jump to the final step, or autoplay once 30% visible that a reader's pause turns off; place it after any `fg:step` listeners. |
| [toggle-bar.css](toggle-bar.css) | Toggle button bar styling, pressed state and focus ring. |
| [toggle-core.js](toggle-core.js) | A `STATES` table (`{ cls, cap, label? }`) driven by one cycling `data-fg="toggle"` button or one button per state, with `tg.show(n)`, `tg.next()` and `fg:toggle` events. |

<!-- inventory:pages:end -->
