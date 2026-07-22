# Slidegen — Product Design Document (v4)

Animated slide generator: HTML/CSS slides rendered to looping GIFs (the only
output format) for embedding in Google Slides. Python CLI, operable by humans
and AI agents.

This document is the implementation spec. It is organized into **phases**, each
independently shippable, each ending with a **manual verification test** that a
human (or agent) runs before starting the next phase. Phases 0–5 constitute
Level 1 of the staged roadmap; Levels 2–3 remain gated behind demonstrated pain
and are summarized at the end so Level 1 code is built in their shape.

## Product decisions (locked)

- **Output: GIF only.** No WebM/MP4 backends at any level. Google Slides
  autoplay-loops GIFs in present mode; that's the target.
- **Quality over size.** Render and encode at full 1600×900 with the
  highest-quality GIF pipeline (256-color per-loop palette, high-quality error
  diffusion dithering). File size is *reported* after encode but never warned
  on and never blocks. No downscaling, no frame decimation.
- **Determinism bar:** two consecutive renders of the same slide are visually
  identical (SSIM ≥ 0.99 per frame). Byte-identical GIFs across machines is a
  non-goal.
- **LLM-first authoring.** Slides are authored (usually by an LLM) against
  `theme/theme.css` + `theme/spec.md`. The tool never calls an LLM API; agents
  operate the CLI from outside.
- **All commands non-interactive**, nonzero exit on failure, actionable error
  messages.

## Repository layout (never changes across levels)

```
slidegen/
├── pyproject.toml            # typer, playwright, pillow, scikit-image (SSIM);
│                             # python ≥3.11; ffmpeg required on PATH
├── slidegen/
│   ├── cli.py                # typer app, thin
│   ├── browser.py            # TimeDriver: deterministic time-stepped capture
│   ├── render.py             # capture orchestration → frames/ → encode
│   ├── encode.py             # GIF encoding (ffmpeg two-pass palette)
│   └── validate.py           # lint + headless dynamic checks
├── theme/
│   ├── theme.css             # color/type/spacing tokens; shared animation classes
│   └── spec.md               # authoring rules for slide authors (human or LLM)
├── slides/                   # 01-intro.html, 02-flow.html, …
├── frames/                   # intermediate PNGs, per-slide subdirs (gitignored)
├── out/                      # GIFs (gitignored or committed, author's choice)
└── tests/                    # pytest; includes the spike fixtures
```

Level 2 adds `slidegen/sheet.py`; Level 3 adds `runtime/choreo.js`,
`slidegen/check.py`, `slidegen/model.py`. Directory shape never changes.

## The one pinned interface: TimeDriver

Everything at every level — render, preview, contact sheets (L2), assertion
checks (L3) — is expressed over this single method. Write it to this signature
from day one and the level climb is purely additive.

```python
class TimeDriver:
    def capture(self, slide_path: Path, times_ms: list[int],
                out_dir: Path) -> list[Path]:
        """Load the slide once, freeze animations before first paint,
        then for each t in times_ms scrub all animations to t and
        screenshot. Returns PNG paths in times_ms order."""
```

Implementation requirements (these are contract, not suggestion):

1. Launch Chromium with `--force-color-profile=srgb --disable-lcd-text
   --hide-scrollbars --force-device-scale-factor=1`; viewport 1600×900.
2. **Freeze before first paint**: inject
   `* { animation-play-state: paused !important; }` via an init script /
   `document_start` stylesheet — *not* after load — so frame 0 has no
   partial-progress bleed.
3. Await `document.fonts.ready`, then one settle pass (double
   requestAnimationFrame) before the first capture, so late layout/font work
   can't leak into frame 0.
4. Per time t: `document.getAnimations().forEach(a => a.currentTime = t)`,
   double-rAF settle, screenshot.
5. Animations still in the `idle` phase (pending `animation-delay`) must be
   scrubbed correctly — the spike fixture explicitly covers this case.

CDP virtual time (the v2 driver) is deliberately not used; keep TimeDriver
small enough that it could be swapped, and build no abstraction beyond the
class boundary above.

## Timing math (house rules)

- `frame_ms` is an integer, a multiple of 10 (GIF frame delays are
  centiseconds; only multiples of 10 ms are exactly representable). Default
  **70 ms**.
- `n = loop_ms / frame_ms` must be an integer; otherwise hard-error listing
  the nearest valid `loop_ms` values.
- ffmpeg framerate is passed as the rational `1000/70` (etc.), never a rounded
  float.
- Frames rendered: exactly `n`, at t = 0, frame_ms, …, (n−1)·frame_ms. The
  frame at t = loop_ms is *not* rendered (it equals t = 0 on a seamless loop).

## Slide contract (Level 1)

- One HTML file in `slides/`, linking `../theme/theme.css` via relative path.
- Root element `<div class="slide" data-loop-ms="6000">`; `.slide` fixes
  1600×900.
- **CSS animations only.** No JS. No CSS transitions (they aren't frozen by
  the pause injection and aren't scrubbed reliably — validate bans them).
- Every animation's `delay + duration × iterations` fits inside
  `data-loop-ms` (machine-checked, see validate).
- Visually identical at t=0 and t=loop (machine-checked via SSIM seam check).
- spec.md documents fill-modes and the quiet-final-500 ms convention.
- Fonts local (`@font-face`, relative url) or system. No network resources.

---

# Phase 0 — Skeleton & environment (½ day)

**Scope**

- `pyproject.toml` (typer, playwright, pillow, scikit-image, pytest;
  python ≥3.11), package skeleton with empty-but-importable modules, repo
  directories, `.gitignore` for `frames/` and `out/`.
- `slidegen doctor` (also run implicitly at startup of every command): checks
  ffmpeg on PATH and Chromium installed for Playwright; prints exact fix
  commands (`playwright install chromium`, distro ffmpeg hint) on failure.
- `theme/theme.css` first cut: color/type/spacing tokens as CSS custom
  properties, `.slide` sizing rule, 2–3 shared animation utility classes.
- `theme/spec.md` first cut: the slide contract above, written for an LLM
  author.

**Manual test (Phase 0 gate)**

```
$ pip install -e . && slidegen doctor
```

passes on a machine with ffmpeg+Chromium, and *fails with the printed fix
hint* (exit ≠ 0) when ffmpeg is renamed off PATH. `python -c "import
slidegen.browser, slidegen.encode, slidegen.render, slidegen.validate"`
succeeds.

---

# Phase 1 — TimeDriver spike (~1 day; do not build past this until it passes)

**Scope**

- Implement `TimeDriver` to the pinned contract in `browser.py`.
- Fixture slide `tests/fixtures/spike.html`: a box animating left→right over
  1000 ms **plus a second box whose animation has `animation-delay: 400ms`**
  (covers the idle-phase scrub case).
- Committed pytest tests:
  1. **Midpoint test**: frame captured at t=500 ms shows box 1 at the
     horizontal midpoint (pixel check with small tolerance).
  2. **Delayed-start test**: at t=200 ms box 2 is at its initial position; at
     t=900 ms it has visibly moved.
  3. **Determinism test**: `capture()` run twice; per-frame SSIM ≥ 0.99.
- If scrubbing captures stale frames, the double-rAF settle is the sanctioned
  fix; re-verify. Any deeper failure stops the project until understood.

**Manual test (Phase 1 gate)**

```
$ pytest tests/test_timedriver.py -v
```

All three tests green. Then eyeball it: open the three captured PNGs and
confirm the boxes are where the tests claim.

---

# Phase 2 — Render & encode (~1 day)

**Scope**

- `render.py`: for a slide, compute `n` from `data-loop-ms` and `frame_ms`
  (hard-error on non-integer division, message lists valid loop values),
  **clean the slide's `frames/` subdir before capture** (stale `%04d.png`
  from a previous longer render must never leak into the GIF), call
  `TimeDriver.capture` for all n times, then encode.
- `encode.py` — quality-first pipeline, ffmpeg two-pass palette:

  ```
  ffmpeg -y -framerate 1000/70 -i frames/{slide}/%04d.png -frames:v {n} \
    -vf "split[a][b];[a]palettegen=stats_mode=diff:max_colors=256[p];\
         [b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle" \
    out/{slide}.gif
  ```

  `sierra2_4a` error-diffusion dithering (best perceptual quality for
  gradients/motion; we don't pay a size penalty because size doesn't matter),
  `diff_mode=rectangle` so static regions stay rock-stable across frames.
  `-frames:v n` belt-and-braces against stale frames. After encode, *report*
  the output size (informational only — no warning, no error).
- Loop metadata: infinite loop flag set (ffmpeg GIF default `-loop 0`).

**Manual test (Phase 2 gate)**

Hand-write a quick slide (any animation) and run the internal render entry
point (CLI arrives in Phase 4; a `python -m slidegen.render slides/…` shim is
fine). Open the GIF in a browser tab: it loops infinitely, motion is smooth at
~14.3 fps, gradients show no visible banding, static text doesn't shimmer.
Render it twice; both GIFs look identical.

---

# Phase 3 — Validate (~1 day)

**Scope** — `validate.py`, two layers:

*Static lint (no browser):*
- `.slide` root present; `data-loop-ms` present, integer, satisfies loop math
  for the configured `frame_ms`.
- No hex/rgb/hsl color literals in the slide file (theme variables only).
- No `transition` properties (banned — not scrubbed).
- No `http(s)://` references; links `../theme/theme.css`.

*Dynamic checks (one headless load, reusing TimeDriver's page):*
- No console errors; computed `.slide` size == 1600×900.
- **Duration check**: read every entry of `document.getAnimations()`; for
  each, `delay + duration × iterations` ≤ `loop_ms`, hard-fail naming the
  offending element/animation. (Infinite iteration counts fail with a message
  explaining the loop model.)
- **Loop-seam check** (promoted from Level 2 — it's ~10 lines given
  TimeDriver): capture t=0 and t=loop; SSIM ≥ 0.995 or fail, writing a diff
  image next to the report.

Every failure message says what to change, in language an LLM author can act
on without seeing the render.

**Manual test (Phase 3 gate)**

Prepare three deliberately broken slides: (a) inline `#ff0000`, (b) an
animation whose `delay+duration` exceeds `data-loop-ms`, (c) an animation
that ends at a different position than it starts (seam break). `slidegen
validate` (or shim) fails each with exit ≠ 0 and a message that names the
exact problem; the seam failure writes a readable diff image. The known-good
Phase 2 slide passes.

---

# Phase 4 — CLI & scaffolding (~½ day)

**Scope** — `cli.py` (typer):

```
slidegen new NN-name              # scaffold slide from template
slidegen render NN-name | --all   [--fps-ms 70]
slidegen validate NN-name | --all
slidegen preview NN-name --at MS  # single frame PNG
slidegen doctor
```

- `new` writes a template slide that already passes validate (linked theme,
  one sample animation, correct loop math).
- `render` runs validate first (fail fast), then render+encode; `--all`
  processes `slides/` in name order, continues past per-slide failures,
  exits nonzero if any failed, prints a summary table.
- `preview --at MS` **snaps MS to the nearest frame boundary and prints the
  snapped value**, so previews always correspond to a real rendered frame.
- `--fps-ms` validated: integer, multiple of 10, divides `data-loop-ms`.
- All commands non-interactive; every failure path exits nonzero with an
  actionable message (agent-usable).

**Manual test (Phase 4 gate)**

```
$ slidegen new 01-demo
$ slidegen validate 01-demo     # passes untouched
$ slidegen render 01-demo       # GIF in out/
$ slidegen preview 01-demo --at 1234   # prints "snapped to 1260" (70ms grid), writes PNG
$ slidegen render --all; echo $?       # 0
```

Then break `01-demo` (inline color) and confirm `render` refuses before
capturing any frames.

---

# Phase 5 — Exit criteria & the real sample (~½–1 day)

**Scope**

- Sample slide `slides/01-sample.html`: title + comet + highlight sweep,
  hand-written CSS against the theme, committed.
- Committed pytest suite covering: the Phase 1 spike tests, loop-math
  validation (valid + invalid cases), the seam check (pass + fail fixtures),
  and an end-to-end render of the sample asserting exactly n frames and a
  nonzero GIF with the loop flag set.
- Determinism as a *committed test*, not just a criterion: render the sample
  twice, per-frame SSIM ≥ 0.99.
- README quick-start: install → doctor → new → validate → render, plus a
  paragraph on embedding the GIF in Google Slides.

**Manual test (Phase 5 gate = Level 1 definition of done)**

1. Fresh clone, `pip install -e .`, `playwright install chromium` →
   `slidegen render --all` produces seamless-looping, high-quality GIFs in
   `out/` with zero manual steps.
2. Drop `out/01-sample.gif` into a Google Slides deck, enter present mode:
   it autoplays, loops without a visible seam, text is crisp.
3. `pytest` fully green.

**Then stop and make the actual presentation.** Levels below are built only
on demonstrated, repeated pain.

---

# Level 2 — Cheap verification (gated)

Trigger: repeatedly rendering full GIFs just to spot-check, or seams slipping
through in ways the automated seam check misses.

- `slidegen sheet NN-name`: one labeled contact-sheet PNG (Pillow grid over
  `TimeDriver.capture` — the pinned interface makes this ~150 lines) at fixed
  intervals plus t=0 and t=loop−frame. One Read instead of twenty.
- `preview --at` gains `--range a:b:step` burst capture.

(The loop-seam SSIM check originally slated here shipped in Phase 3.)

# Level 3 — Choreography runtime (gated, spec: v2 doc §3–§5)

Triggers: hand-fixing motion-path coordinates for the Nth time; motion feel
drifting between slides; LLM-authored slides needing multiple
visual-inspection rounds each.

- `runtime/choreo.js`: semantic choreography via `data-choreo-*`; five named
  patterns (`reveal`, `volley`, `flare`, `sweep`, `payoff-hold`);
  beat-quantized timing; geometry from `getBoundingClientRect` (kills
  coordinate guessing); release-before-loop window; compiles to CSS
  animations; exports `window.__choreo` timeline as the contract.
- `check.py`: assertions auto-derived from the exported timeline, evaluated by
  time-stepping computed styles via `TimeDriver` — LLM iteration becomes
  assertion-driven, no vision needed.
- `validate` learns the choreography vocabulary; raw CSS animation becomes a
  warning (escape hatch).

Effort honesty: choreo.js is larger than all Level 1–2 Python combined and
needs browser-side unit tests. That is exactly why it is gated.

# Out of scope (all levels)

- WebM/MP4/any non-GIF output.
- Size optimization of any kind (downscaling, frame decimation, palette
  starvation) — quality wins.
- Style harvesting from existing GIFs.
- LLM API integration inside the tool.
- Editing Google Slides files; cross-machine byte determinism.
