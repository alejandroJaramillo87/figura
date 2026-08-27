# Hero art direction — choosing a treatment

Heroes are the one kind in this library where the *style* is an open
question. A step-timeline looks the way step-timelines look; a hero
could be almost anything. This doc is about making that choice on
purpose.

Nothing here is enforced. `scripts/validate.js` checks scoping,
tokens, keyframes, ids, accessibility and the hero lifecycle — all
style-neutral. The rules in [CLAUDE.md](../CLAUDE.md) are the contract,
[authoring.md](authoring.md) is how to make a piece look like the
library, and `tools/heroes/README.md` is the generator pipeline. This
doc is the layer above all three: *which treatment, and why that one*.

**Scope.** This serves the art-style showcase (`showcase.html`,
`post: "showcase"` in the manifest). It is not a policy for the posts
already written, and it makes no recommendation about whether style
should be picked per post, per series, or once for the whole blog.
That decision comes after the showcase exists and there is something
real to choose between.

---

## 1. Subject, theme, treatment

Art directors split a brief into three layers, and most muddled style
decisions come from collapsing them:

- **Subject** — what is literally depicted. *A desk with a monitor at
  night.*
- **Theme** — what it is *about*. *Solitary craft; the machine working
  while you sleep.*
- **Treatment** — the stylistic and technical approach applied. *Pixel
  art, 8-unit cell grid, three-band `--px-*` ramps, `steps()` motion.*

The question this doc answers is which **subjects and themes** each
**treatment** can carry. Matching those is called **art direction**,
and it is a separate skill from executing the art itself.

---

## 2. The axis that does the work

The most useful single concept here is **diegesis**.

- A **diegetic** image depicts a coherent world you could stand inside.
- A **schematic** image arranges symbols that stand for things.

Every treatment sits somewhere on that spectrum, and mostly it is not a
choice — it is baked into the medium.

A **conceit** is a borrowed-structure metaphor: "X as Y." A motherboard
as a city is a conceit.

> **The rule: the more diegetic a treatment, the worse it holds a
> conceit.** The depiction wins and the second reading never arrives.
> Schematic treatments hold double readings comfortably, because the
> viewer is already in "this is a representation" mode.

This library ships both halves of the worked example, so the claim is
checkable.

### `workstation-night` — the fit lands

Three things agree:

1. **Grain match.** Everything that must be legible — monitor, chair,
   tower, window, lamp — is far bigger than one 8-unit cell.
2. **Diegesis is the point.** The brief *wants* a place. The most
   diegetic treatment in the library is the right tool.
3. **Register match.** Pixel art's nostalgic warmth is exactly the tone
   of solitary night work.

### `motherboard-city` — the conceit does not survive

This piece is well-built and technically clean. The mismatch is in the
brief, not the execution — and it is the case that prompted this doc.

1. **Grain mismatch.** Traces, pins and pads are sub-cell on a 150-cell
   canvas. The subject's meaningful detail is finer than the medium's
   smallest mark, so it cannot be rendered at all.
2. **Diegetic override.** Pixel art builds worlds too well. You read a
   city — districts, a harbor, an avenue with headlights — and the
   motherboard survives only as a caption. The generator's own docstring
   ("CPU heatsink downtown, RAM tower blocks, VRM industrial district,
   trace-road streets") is a list of mappings the image cannot actually
   assert; the finished `aria-label` describes a city and hedges the
   hardware into "trace-like roads."
3. **Register mismatch.** A warm, nostalgic, humanist treatment has been
   asked to carry a cold structural claim about hardware topology.

Any one of these is a warning. All three is a piece that reads as
something other than what it is about.

**Note what this does *not* say.** The conceit is fine; the *treatment*
is wrong for it. Motherboard-as-city in **isometric vector** would work,
because that projection is already the language of technical
explanation, so the double reading is available rather than suppressed.
Same idea, different medium, opposite outcome.

---

## 3. Vocabulary

| term | meaning | why it matters here |
|---|---|---|
| **grain** / **the mark** | the smallest unit the medium can place — pixel, facet, stroke, particle | sets the **detail budget**; if the subject's meaningful detail is finer than the grain, change treatment |
| **register** | the tone a visual language carries by default | nostalgic, clinical, editorial, monumental — inherited whether or not you want it |
| **iconographic baggage** | the cultural priors a style drags along | pixel art = 8-bit games; isometric = SimCity plus SaaS explainer; blueprint = patent drawings |
| **silhouette read** | can you identify it from the black shape alone? | the pass/fail test for pixel art and low-poly |
| **notan** | the arrangement of light and dark masses, ignoring detail | how you know a composition works before rendering anything |
| **facture** | visible evidence of how the thing was made | pixel and plotter art are high-facture; flat vector is low |
| **axonometric** | the family of parallel projections | **isometric** is one member (equal foreshortening on all three axes); dimetric and trimetric are the others |
| **parallel vs. perspective projection** | no vanishing point vs. a vanishing point | parallel means no depth hierarchy and no scale drama — the reason isometric reads as inventory rather than drama |
| **limited animation** / **on twos** | moving few elements, on held frames | what `steps(N)` flipbook loops and `var(--dur-tick)` already do |
| **idle cycle** vs. **one-shot** | perpetual loop vs. single beat | the `.is-settled` ambient loop vs. the intro choreography |
| **diegetic vs. non-diegetic motion** | the world moves vs. the graphic presents itself | a fan spinning vs. a stagger-in wipe |
| **thumbnail test** | does it read at 200px while scrolling past? | heroes are always seen at a glance first |

---

## 4. Motion means something different in each treatment

Motion is not a garnish added at the end. Each medium has a native thing
that motion *means*, and fighting it reads as noise — which is the same
instinct behind the library's "effects must explain" rule.

| treatment | motion means |
|---|---|
| pixel art | **life** — a fan turns, a cursor blinks, rain falls |
| isometric vector | **assembly and flow** — things build; things travel the lattice |
| flat-shaded low-poly | **form revealed** — you orbit to understand the shape |
| line-art / plotter | **derivation** — the line being drawn *is* the argument |
| generative | **process** — the system running forward in time |

The existing hero lifecycle already splits along this seam, which is
worth naming explicitly:

- `.is-live` — the **intro** is *non-diegetic*. The graphic is
  presenting itself. This is why the dense-staggered-entrance carve-out
  in CLAUDE.md is coherent rather than a loophole: intro motion is
  allowed to be about the artwork.
- `.is-settled` — the **ambient loop** is *diegetic*. The world is
  living. This is where the ≤3-concurrent rule bites, and why ambient
  motion has to belong to the depicted world rather than to the frame.

A treatment whose native motion is *derivation* or *process* will strain
against that split, because for those the "ambient" state is the whole
point and the intro is arbitrary.

Building the generative piece settled that for one case, in its favour.
An attractor gets a non-arbitrary reading for all three states — the
intro is the trajectory integrating forward, `.is-settled` is the
attractor set it converged onto, and the ambient loop is the orbit still
being traversed. Where a process treatment *can* map its lifecycle like
that, the split stops being a tax. Still worth watching for line-art.

---

## 5. The five treatments

Status is explicit because two of these do not exist yet. Nothing below
except pixel art, isometric vector and generative describes shipped
capability.

### Pixel art — **shipped, house style**

**Grain** one 8-unit cell (150 across a 1200 viewBox) · **register**
warm, nostalgic, humanist, hand-made · **baggage** 8/16-bit games,
demoscene, terminal culture

**Carries well** — place, mood, character, interiority. The
human-machine relationship. Night work, vigil, the machine running while
you are not looking. Craft and tinkering. It is the only treatment here
that can render a *figure* with warmth.

**Fails at** — content-as-the-point. Architecture, quantity, fine
structure, anything needing a label. The coarse grain kills detail, and
the nostalgic register sentimentalizes cold claims. Conceits die in it
(§2).

**Test** — *could you set a short story in this image?* If yes, pixel
art. If the image is an argument rather than a place, no.

**Build cost** — known, and the highest per piece. Hand-placed ASCII
maps via `herolib.py`. It is also the only treatment with a **width
constraint**: `.post-hero--figura` pins to 1050px because the 150-cell
grid only lands on whole pixels at multiples of 150 (1050 = exactly 7px
per authored pixel at dpr 1). `npm run test:hero-grid` enforces it.

### Isometric vector — **portfolio, one piece, unadopted**

**Grain** the polygon, and **scale-free** · **register** clear,
systematic, explanatory but friendly · **baggage** SimCity and Transport
Tycoon, IKEA assembly diagrams, exploded parts drawings, architectural
axonometric, the 2015–2020 SaaS-landing-page wave

**Its distinguishing property** — isometric holds a *place-reading* and
a *system-reading* at the same time. A datacenter in isometric is both a
room you could walk through and a diagram of a system. This is the one
treatment that makes conceits available rather than suppressing them.

**Carries well** — systems with spatial structure. Memory hierarchy as
stacked floors. Cache as shelves filling. Racks and aisles. Transformer
layers as a literal stack. Pipelines as conveyors. Routing between
places. Assembly over time — a training run *building* something. The
whole machine-as-habitat family, motherboard-city included.

**Fails at** — organic form and drama. The lattice is both its strength
and its prison: anything off-axis looks wrong or costs enormous polygon
count. Faces become chibi tokens, not characters. And parallel
projection means **no depth hierarchy**, so nothing can be made to feel
*vast*.

**Build cost** — known and low, now that `isolib.py` exists. Painter's
order is free (`x + y + z` ascending), face culling is mechanical, and
`prism()` collapses any box to 3 polygons. **No width constraint** —
polygons scale cleanly at any display width, unlike pixel art.

### Flat-shaded low-poly — **proposed**

**Grain** the facet · **register** monumental, cool, contemplative ·
**baggage** the 2013–16 flat-3D trend, Monument Valley, topographic and
geological rendering, fintech brand illustration

**Key difference from isometric** — perspective projection and a free
camera. That buys depth hierarchy, scale drama, and makes camera
movement itself a motion vocabulary.

**Carries well** — a single form, beheld. One hero object on an empty
stage: a chip, a crystal, a mesh. **Terrain is its home turf** — a loss
landscape as faceted topography with descent tracing across it. Topology
and manifolds. Monumentality, because perspective can make something
feel big.

**Fails at** — many small parts (facet count explodes), labels, dense
scenes. A treatment for beholding, not reading.

**Build cost** — **highest, by a wide margin.** It needs a mesh pipeline
the repo does not have: geometry generation, normals, camera transform,
and a real depth sort (the free `x + y + z` ordering that makes
isometric cheap does not exist off the lattice). It is also the one
treatment likely to need **new palette tokens** — three shading bands is
a hard floor for faceted lighting — and `--px-*` is a closed set the
validator enforces, so that change also touches `shared/tokens.css` and
the blog's `scripts/check-figura-tokens.mjs`. Do not start here.

### Line-art / plotter — **proposed**

**Grain** the stroke — and note the detail budget is *high*, because a
1px stroke stays legible where a 1px fill does not · **register**
analytical, precise, authoritative · **baggage** patent illustration,
Da Vinci's notebooks, blueprints, Tufte, oscilloscope traces, AxiDraw
plotter culture

**Motion is its superpower** — draw-in is the only animation here that
carries meaning intrinsically: the line being made *is* thought being
worked out.

**Carries well** — structure and relation. Graphs, topologies, the
actual shape of an architecture. Cross-sections and cutaways.
Mechanistic interpretability is almost purpose-built for it — circuits,
paths, ablations. Conceits land, because the register is already
abstract.

**Fails at** — mood, warmth, mass. Nothing feels lived-in; there is no
value structure, so you cannot do a dark room. Overused it reads cold.

> **⚠ The discipline caveat.** Line-art heroes **compete with figura's
> own diagrams**. CLAUDE.md says heroes are abstract art, not
> explanation — no labels, no diagram anatomy. A blueprint hero sitting
> above a blueprint figure collapses that distinction and the hero stops
> being art. Of the five, this one needs the strictest restraint about
> staying evocative.

**Build cost** — low. Stroke-only SVG needs no new machinery, and the
draw-in pattern already exists in `shared/effects.css`
(`stroke-dashoffset`, with its reduced-motion fallback). The work is
authoring geometry, not building a pipeline.

### Generative / algorithmic — **portfolio, two pieces, unadopted**

**Grain** the particle, agent or cell — but the real unit is **the
field, not the object** · **register** rigorous, cool, contemporary ·
**baggage** Vera Molnár, Casey Reas and Processing, flow-field plotter
art, Art Blocks, demoscene

**Family** — flow fields, reaction-diffusion, noise fields, L-systems,
cellular automata, strange attractors, moiré, packing and subdivision.

**Carries well** — behavior, not things. **Emergence** is the single
best fit: simple rules producing complex behavior. Distribution and
density. **High dimensionality** — the only treatment that can honestly
gesture at a space too big to draw. Training dynamics: annealing,
convergence, phase transitions. Noise, sampling and temperature, where
the stochasticity *is* the subject.

**Fails at** — anything specific. It cannot point at *this* cache or
*this* kernel. It also carries the highest risk of decorative drift,
because generative work is very easy to make pretty and very hard to
make mean something — precisely the failure mode the "effects must
explain" rule exists to prevent.

**The discipline that saves it** — bind the parameters to the subject.
Drive the field from a curve that actually belongs to the topic. Then it
is not wallpaper.

**Build cost** — **lowest, and it held up twice.** `strange-attractor`
is 39 KB from a 49-line generator and `truchet-loops` 22 KB from 63
lines: pure rules to SVG paths, no asset pipeline, no ASCII maps, no
mesh, and no new tokens for either. The family claim is now evidenced
rather than asserted — the second piece reused `genlib` wholesale and
cost one generator and one template, which is why the showcase stacks
both under a single section. **Range is nearly free once the module
exists**, and it is real range: the two look nothing alike.

**What the second piece bought that the first could not.** The attractor
is deterministic chaos and convergence; it never touched **emergence**,
which this section calls the treatment's single best subject. A random
Truchet tiling is the clean case — one coin flip per cell, and the
loops that chain out of it have a heavy-tailed size distribution nobody
put there. The two also divide the treatment's motion vocabulary
between them: the attractor's reveal is a trace, because its parameter
is time; the tiling's is a staggered hard cut ordered by loop size,
because what it has to show is a distribution. A second trace piece
would have been a different image making the same argument.

Four things cost more than the estimates did, and all are now in
`tools/heroes/README.md`:

- **An SVG dash pattern restarts at every subpath.** The obvious
  structure — one path per depth band — makes each path ~100 disjoint
  runs, and `stroke-dashoffset` then fills them in parallel from
  arbitrary offsets instead of tracing anything. The fix is to cut the
  trajectory into *chronological* runs, one subpath per element, and
  colour each by the depth stratum it sits in. That buys a real
  draw-in, `--i` chronology, and the depth read at once, but it is 150
  elements rather than 3.
- **These attractors do not fit a 12:5 frame.** The widest orientation
  of any system in `SYSTEMS`, found by searching a lattice of rotations,
  projects 1.85:1 against the frame's 2.4:1. The view has to be searched
  rather than eyeballed, and the form fitted to height so it runs to the
  edges. (A tiling has the opposite problem, which is to say none: pick
  a grid that divides the frame and composition is settled.)
- **Stochastic output needs a determinism rule.** Everything before this
  treatment was reproducible for free. A tiling is not, and
  `npm run heroes` regenerates the whole library on every run, so all
  randomness has to go through a seeded `random.Random` or the working
  tree churns whenever anyone touches an unrelated hero.
- **Strata cut on terciles put a third of the ink in the top band**, and
  the first render of `truchet-loops` came out reading as mostly
  highlight rather than as a field with one bright object in it. Loop
  sizes are heavy-tailed; the cut belongs in the real gap in the
  distribution, which has to be measured before it can be chosen.

---

## 6. The selection heuristic

Run these in order.

1. **What is the piece about?** Place or experience → pixel. System with
   structure → isometric. Form or shape → low-poly. Relation or
   derivation → line-art. Behavior or distribution → generative.
2. **What is the smallest thing that must be legible?** Smaller than the
   treatment's grain → change treatment. This alone would have caught
   motherboard-city.
3. **Depiction or conceit?** Conceits need schematic treatments
   (isometric, line-art, generative). Diegetic ones (pixel, low-poly)
   kill them.
4. **What should the motion mean?** Life / assembly / form / derivation
   / process — pick the treatment whose native motion matches (§4).
5. **Does it fight the figures below it?** A hero that reads as a
   diagram is not a hero.

### Cheat sheet

| treatment | diegetic ←→ schematic | native motion | best subject | worst subject |
|---|---|---|---|---|
| **pixel** | strongly diegetic | life | place, mood, character | structure, quantity, conceits |
| **isometric** | **both at once** | assembly, flow | spatial systems, layers, habitats | curves, fields, drama, faces |
| **low-poly** | diegetic, object-scale | form revealed | terrain, one hero object, manifolds | dense scenes, labels, fine detail |
| **line-art** | schematic | derivation | topology, cross-section, circuits | mood, warmth, mass |
| **generative** | schematic → abstract | process | emergence, distribution, high-dim | anything specific |

---

## 7. What the library actually costs

Measured, for calibration when scoping a new piece.

| hero | treatment | output | shapes | generator |
|---|---|---|---|---|
| `brain-chip` | pixel | 24 KB | 198 rects | 155 lines |
| `workstation-iso` | isometric | 26 KB | **151 polys** | **144 lines** |
| `hooded-hacker` | pixel | 36 KB | 361 rects | 123 lines |
| `truchet-loops` | generative | **22 KB** | 69 paths | 63 lines |
| `strange-attractor` | generative | 39 KB | 150 paths | **49 lines** |
| `motherboard-city` | pixel | 64 KB | 656 rects | 268 lines |
| `workstation-night` | pixel | 75 KB | 813 rects | 341 lines |
| `training-net` | pixel | 228 KB | 2,940 rects | 196 lines |

Two readings worth keeping:

- **Pixel art has a complexity ceiling.** `training-net` is 228 KB and
  nearly 3,000 rects — an order of magnitude past the others. Scene
  density in pixel art costs output size linearly and there is no
  mechanism to amortize it.
- **The generative generators are the shortest in the library**, at 49
  and 63 lines against pixel art's 123–341, and it is the only treatment
  where scene complexity does not come out of the author's hands:
  raising the run count or swapping the algorithm changes the picture
  completely without changing the generator's length.
- **The second piece in a treatment is far cheaper than the first.**
  `truchet-loops` is the smallest hero in the library at 22 KB, and its
  63-line generator sits on machinery `strange-attractor` had already
  paid for — the marginal cost of range, once a module exists, is one
  generator and one template.
- **`workstation-iso` is the A/B.** Same subject as
  `workstation-night`, one third the output, 151 shapes against 813, and
  a shorter generator — because `prism()` collapses a desk top to 3
  polygons where voxels would need hundreds. Style was the only variable.

---

## 8. Build order for the showcase

Sequencing for the unbuilt treatments, weighing cost against how much
range each adds.

1. ~~**Generative**~~ — **built** (`strange-attractor`). It was picked
   first for being the cheapest and the furthest from anything else in
   the library, and both held: 39 KB from the shortest generator here.
   Of the four generative forms considered — attractors, flow fields,
   reaction–diffusion, Voronoi — attractors won on three counts. Their
   motion *is* the algorithm rather than a presentation device; they are
   the cheapest by element count (flow fields want 200–600 streamlines);
   and they are the literal family case, since swapping the ODE changes
   the picture completely. Two were ruled out on grounds worth keeping:
   **Voronoi collides with low-poly** (flat polygons shaded by distance
   is what that treatment promises, and a showcase whose thesis is that
   treatments differ should not ship two that look alike), and
   **reaction–diffusion needs numpy**, which would be the repo's first
   Python dependency. If the topographic contour look is wanted later,
   Chladni nodal lines give it from a closed-form function.

   A second piece followed, `truchet-loops`, for two reasons that are
   worth separating from the first pick. It covers **emergence**, which
   §5 names as the treatment's best subject and which an attractor does
   not touch; and it is the evidence for the family claim that made
   generative go first at all — 22 KB from a 63-line generator, reusing
   `genlib` whole. Of the forms considered for it, harmonograph was the
   cheapest and was passed over precisely because it is *mechanically*
   the attractor again (a decimated polyline traced by
   `stroke-dashoffset`); a second trace piece would have made the same
   argument with a different picture. Flow fields were passed over as
   the heaviest and most iconographically loaded, and diffusion-limited
   growth because it reads in the same organic register as the
   attractor and its random walks are slow in pure Python. Still in the
   pool for later: Chladni nodal lines, Truchet's discrete cousins
   (Wang tiles), percolation at threshold, and space colonization.
2. **Line-art** — cheap, and draw-in already exists. Next, but it needs
   the discipline caveat resolved first (see §9), or the piece risks
   reading as a diagram rather than a hero.
3. **Low-poly** — a real toolchain investment plus a probable token
   change spanning both repos. Decide only after line-art lands, and
   only if the range covered turns out to have a hole shaped like
   terrain and monumentality.

---

## 9. Open questions

**The explanation wall — still open.** CLAUDE.md says heroes are
abstract art — no labels, no literal diagram anatomy. The schematic
treatments (line-art especially, isometric to a degree) pull hard
against that, because their whole power is holding a structural
reading. Does the wall hold, or do schematic treatments get to be
semi-explanatory? Answering "the wall holds" is a real constraint on
what line-art may depict, and line-art is next, so this is the one to
settle first. Generative did not test it: an attractor has no labels
and no diagram anatomy either way.

**Showcase framing — settled by force.** The question was whether the
showcase is a same-subject A/B (what `workstation-iso` does, re-doing a
pixel hero so treatment is the only variable) or best-case-per-style.
Generative decided it: there is no generative rendering of "a
workstation at night" that is not absurd, so the A/B was simply
unavailable. The page is therefore **one controlled comparison plus a
range demonstration** — `workstation-iso` against `workstation-night`
proves the treatments are comparable, and every piece after it takes
the subject its treatment is strongest at. That is a better page than
either pure framing, and it is the standing rule for line-art and
low-poly.
