# Hero generators

The pixel-art heroes are not hand-edited HTML — each is a generator +
template pair in this directory, sharing common machinery from
`herolib.py`:

- `<name>.py` — the scene: ASCII pixel maps, sprite geometry, animation
  class hooks. Imports everything from `herolib` (never copy helpers or
  extend `COL` locally).
- `<abbr>-template.html` — the choreography: keyframes, lifecycle state
  CSS, aria-label, `INTRO_MS`. Managed sentinel blocks ship empty and
  are expanded by `scripts/build.js`.

| hero | generator | template |
|---|---|---|
| `diagrams/linux-ai-setup/workstation-night.html` | `workstation-night.py` | `wsn-template.html` |
| `diagrams/linux-ai-setup/motherboard-city.html` | `motherboard-city.py` | `mbc-template.html` |

## Pipeline

1. Scaffold a new hero pair (also creates the diagram file and the
   manifest entry):

   ```
   node scripts/new-diagram.js <post-slug>/<kebab-name> \
     --kind hero --abbr <2-6 char prefix> --title "Title"
   ```

2. Edit the generator (scene geometry, sprites) and the template
   (keyframes, state CSS, aria-label). Never edit the generated diagram
   file directly — it is overwritten.
3. Regenerate: `python3 tools/heroes/<name>.py` for one hero, or
   `npm run heroes` for the whole library (either way, run
   `node scripts/build.js` after a lone generator run to re-expand the
   managed blocks — `npm run heroes` does it for you).
4. `npm run check`, then preview in a browser / the gallery.

## Generator conventions

- 1 cell = 8 viewBox units; a 1200×500 hero is a 150×62 cell canvas.
- The palette character alphabet lives in `herolib.COL` and is
  **canonical**: chars map to ramp/dim tokens (`1-4` steel, `a/b/c`
  amber, `g/G/e` green, `s/S/k` sky, `p/r/h` dusk, `y/Y/z` violet,
  `x/X/Z` ember, `o` outline, plus the base/dim tokens). New chars are
  added to `herolib.py` — never per generator.
- The `--px-*` ramp tokens in `shared/tokens.css` are a **closed set**:
  new heroes compose from the existing ramps; ramp tokens are never
  added per hero (the validator rejects unknown `var(--px-*)` refs).
- Helpers (all from `herolib`): `rects(ox, oy, rows)` for ASCII maps
  (`.` = transparent; horizontal same-color runs merge into single
  `<rect>`s), `rect(...)` for singles (supports `cls`/`style` for
  animation hooks like `class="wsn-pop" style="--i: 2"`),
  `dither(...)` / `dither_row(...)` for 2-cell checker transition rows,
  `emit(template, out_relpath, sprites)` to write the diagram.

## Choreography contract (template side)

Lifecycle classes are driven by the `hero-start` managed block:
`.is-live` fires the intro once per page load at ~30% visibility;
`.is-settled` is added after `INTRO_MS` (immediately under
`prefers-reduced-motion`) and gates the ambient loop; `.is-paused`
toggles while off-screen — map it to `animation-play-state: paused`.
The `.is-settled` rules alone must render the complete final
composition: that is the reduced-motion rendering.

Pixel-art rules: `shape-rendering: crispEdges`, no `rx`, no filters, no
pattern fills, no plain opacity fades — reveals hard-cut with
`steps(1, jump-start)` + delay (a `jump-end` at exactly 100% can be
missed to float error); multi-stutter keyframes use paired holds so the
last interval's start value equals the settled value. Motion is
frame-quantized via `var(--ease-frames)` / `var(--ease-frames-coarse)`
and `var(--dur-tick)`-based `steps(N)` flipbook loops. Full contract:
CLAUDE.md (hero section).

## Sync enforcement

Animation classes attached in the generator must match CSS rules in the
template — the validator enforces this symmetrically on the generated
file (`hero-sync`), checks settled-state completeness (`hero-settled`),
and catches an unsubstituted `@SPRITES@`. Escape hatches, declared in a
template CSS comment:

- `/* fg:sync-exempt <class> [<class> …] */` — structural grouping
  classes whose frame variants carry the rules (e.g. `wsn-rain` with
  `wsn-rain-1/2`).
- `/* fg:settled-exempt <class> */` — intro-only one-shots that
  legitimately have no `.is-settled` rule.
