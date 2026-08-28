# Hero generators

The pixel-art heroes are not hand-edited HTML — each is a generator +
template pair in this directory, sharing common machinery from
`herolib.py`:

- `<name>.py` — the scene: ASCII pixel maps, sprite geometry, animation
  class hooks. Imports everything from `herolib` (never copy helpers or
  extend `COL` locally).

`herolib.py`, `isolib.py` and `genlib.py` are shared machinery, not
scenes:
`scripts/heroes.js` skips them by name (`LIBS`). A new shared module must
be added to that set or `npm run heroes` will try to run it as a
generator.
- `<abbr>-template.html` — the choreography: keyframes, lifecycle state
  CSS, aria-label, `INTRO_MS`. Managed sentinel blocks ship empty and
  are expanded by `scripts/build.js`.

| hero | generator | template |
|---|---|---|
| `diagrams/linux-ai-setup/workstation-night.html` | `workstation-night.py` | `wsn-template.html` |
| `diagrams/linux-ai-setup/motherboard-city.html` | `motherboard-city.py` | `mbc-template.html` |
| `diagrams/sandboxing/training-net.html` | `training-net.py` | `tnet-template.html` |
| `diagrams/showcase/workstation-iso.html` | `workstation-iso.py` | `wiso-template.html` |
| `diagrams/showcase/strange-attractor.html` | `strange-attractor.py` | `atr-template.html` |
| `diagrams/showcase/truchet-loops.html` | `truchet-loops.py` | `trl-template.html` |
| `diagrams/showcase/stochastic-net.html` | `stochastic-net.py` | `snet-template.html` |
| `diagrams/showcase/coarse-grain.html` | `coarse-grain.py` | `cgr-template.html` |

This file is the mechanical pipeline. For *which* art treatment a new
hero should use — and what each candidate style costs to build — see
[docs/hero-art-direction.md](../../docs/hero-art-direction.md).

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

## Isometric-vector heroes (`isolib.py`)

A second hero art style, kept in the portfolio (`showcase.html`,
`post: "showcase"` in the manifest) rather than adopted for any post yet.
It ships under the existing `kind: hero` — the lifecycle contract,
managed blocks and validator rules are all style-neutral, and the
pixel-art rules above (`crispEdges`, no `rx`, no opacity fades, 8-unit
cells) are prose, not enforcement. Reference: `workstation-iso.py` +
`wiso-template.html`, the workstation-night scene rebuilt in the style.

Volumes on a 3D lattice, projected to flat-shaded polygons:

- 1 cell = `isolib.S` viewBox units (a generator may raise it to scale a
  scene; `workstation-iso` uses 17). y is up.
- **Two primitives, and picking the right one is the whole size story.**
  `prism()` is 3 polygons for a box of any size — use it for anything
  regular (desk, wall, tower, floor). `voxels()` + `iso()` culls face by
  face against neighbours, for detail clusters whose shape genuinely
  varies cell by cell. A desk top voxelized is 220 polygons; as a prism
  it is 3.
- Only three faces are ever visible (+y top, +x down-right, +z
  down-left), and `RAMP` maps a character to that triple — top
  highlight, right mid, left shadow. Every `--px-*` ramp already has
  exactly three bands, so **no new tokens are needed** and the closed set
  stays closed. `RAMP` is canonical the way `herolib.COL` is: new
  characters map to existing ramps or are not added.
- Painter's order for lattice boxes is `x + y + z` ascending — `iso()`
  sorts for you, but `prism()` output is emitted in call order, so a
  generator composes back to front itself.
- Seams between adjacent same-colour faces are closed geometrically
  (`isolib.INFLATE` overscales each face about its centroid), never with
  strokes. Templates use `shape-rendering: geometricPrecision`, not
  `crispEdges`.
- Lit surfaces take a flat `tone=` override instead of a ramp: light
  reads flat, not faceted.

Choreography. Prisms join the intro wave via `--i` taken from the box's
centre depth (`x + z`), so the scene assembles back to front; `iso()`
takes `wave_base=` so a voxel cluster staggers on that same clock rather
than its own local minimum. Keep the class set small and fixed — vary
`--i` through the inline `style`, never by minting classes — or
`hero-sync` will drift on every regeneration.

Composition. An isometric floor always projects 1.73:1, so a footprint
wide enough to fill a 2.4:1 hero is far too tall. Lay scenes out along
the **anti-diagonal**: screen-horizontal is `u = x - z` and
screen-vertical is `v = x + z`, so spreading props over `u` costs nothing
vertically. Solve the framing numerically (`isolib.extent()`) and let the
floor and walls bleed off the edges.

## Generative heroes (`genlib.py`)

A third hero art style, also portfolio-only (`showcase.html`,
`post: "showcase"`). Same deal as the isometric style: `kind: hero`, the
lifecycle contract and validator rules are style-neutral, and the
pixel-art rules above are prose. Reference: `strange-attractor.py` +
`atr-template.html`.

Nothing is placed by hand: a rule runs and its output is emitted as
`<path>` elements that CSS draws. Two families live in `genlib` —
**attractors** (continuous, deterministic: integrate, project, decimate,
cut into runs) and **tilings** (discrete, stochastic: fire a rule per
cell and chain whatever connects). `SYSTEMS` is canonical the way
`herolib.COL` and `isolib.RAMP` are: a new attractor is added there,
never redefined in a generator. Everything is stdlib — this style does
not introduce the repo's first Python dependency, and should not.

**Randomness goes through a seeded `random.Random`, never the module-level
`random` functions.** `npm run heroes` regenerates the whole library on
every run, so a generator that is not reproducible churns the working
tree every time anyone touches an unrelated hero — and `build --check`
diffs the result in CI. Prefer `.randrange()` / `.random()` over
`.choice()` / `.shuffle()`, whose implementations have moved between
Python versions. Verify by regenerating twice and diffing.

- **One subpath per element, always.** An SVG dash pattern restarts at
  every subpath, so `stroke-dashoffset` on a path made of many runs does
  not trace it — it fills each run in parallel from an arbitrary offset,
  and a `stroke-dasharray` "point" becomes one point *per run*. This is
  the single biggest trap in the style; both bugs look like a working
  animation until you step the frames.
- **Cut chronologically, colour by depth.** `runs()` slices the
  trajectory into equal spans of *time*, each tagged with the depth
  stratum it passes through. That gives one subpath per element (so the
  draw-in is a real trace), `--i` carrying chronology to CSS, and a
  three-tone depth read from one `--px-*` ramp — three strata against
  three bands, so **no new tokens** and the closed set stays closed.
- Coordinates round to whole viewBox units in `path_d()`; float noise is
  the biggest cause of bloated output. Decimation tolerance is in
  viewBox units — 0.8 is imperceptible at hero width and ~15% smaller
  than 0.6.
- `decimate()` is iterative on purpose: a recursive Ramer–Douglas–Peucker
  blows Python's recursion limit on a 20k-point trajectory.
- Templates use `shape-rendering: geometricPrecision`, not `crispEdges`.

Choreography. The intro draws the runs in order via
`animation-delay: calc(var(--i) * <unit>)`, and it runs `linear` rather
than an easing token — the draw rate is the integration rate, so an
eased curve would misreport how the system runs. The `.is-settled` rule
has to restate `stroke-dashoffset: 0`: it replaces the intro animation,
and with it the `both` fill that was holding the curve drawn. Keep the
class set to the run class plus one per stratum and vary `--i` inline,
or `hero-sync` drifts on every regeneration.

Composition. These attractors are all roughly isotropic — the widest
orientation of any system in `SYSTEMS` projects about 1.85:1 against a
2.4:1 frame — so the view is searched, not eyeballed: rotate over a
lattice of angles and take the widest projection, then `fit='height'` to
run the form to the edges. `project()` has no stretch mode on purpose;
distorting a mathematical object to fit a frame is a lie about its
shape.

### Tilings

`truchet_arcs()` rolls one orientation per cell and emits the arcs;
`chain()` walks them into components; `arc_d()` writes one as a subpath.
Reference: `truchet-loops.py` + `trl-template.html`.

- **`chain()` is a walk, not a union-find.** Every edge midpoint is
  shared by at most two cells, so every node has degree ≤ 2. Take the
  open runs first, from the degree-1 nodes at the field boundary; what
  is left is closed loops.
- **Cells passed to `skip` are still rolled**, then dropped, so changing
  the skip set does not reshuffle the rest of the field. Their edge
  midpoints become loose ends — which is what you want if the cells are
  meant to read as undecided, as `truchet-loops` uses them for its
  ambient.
- **Cut strata on the measured distribution, not on terciles.** Loop
  sizes are heavy-tailed: at `truchet-loops`' seed they run
  … 24, 27, 38, 96. Equal-count terciles put a third of the ink in the
  top band and the piece rendered as mostly highlight; cutting in the
  real gap leaves the giant loop alone up there at 20% against a 56%
  body and a 23% haze. Print the distribution before choosing.
- The bottom band of a `--px-*` ramp is not equally legible across
  ramps. `--px-violet-1` sits at about 1.5:1 on the panel against
  `--px-sky-1`'s 3.06:1, so a field drawn in it needs a little extra
  stroke width to stay present rather than vanishing.

Choreography. A tiling's reveal is **not** a draw-in — the attractor
already owns tracing, and a component is one element, so it cannot wave
in spatially anyway. `truchet-loops` hard-cuts one component per tick
ordered smallest-first, which assembles the size distribution rather
than a path, and holds the largest back an extra beat so the field
finishes with a visible hole where it will land. Anything that animates
under `.is-live` needs a matching `.is-settled` rule, the size classes
included — the validator will tell you.

Composition. Unlike the attractors there is nothing to search: pick a
grid that divides the frame (24×10 cells of 50 units fills 1200×500
exactly). The seed picks *which* picture, not whether there is one —
every seed tried gave a giant component carrying 10–28% of the ink — so
choose it for where that component runs, and verify the giant survives
the `skip` cells, which can split it.

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
