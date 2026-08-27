"""Strange attractor — the generative/algorithmic hero style study.

Halvorsen's attractor, RK4-integrated for 26k steps, projected to the
plane and cut into chronological runs. CSS then draws the runs in order
with stroke-dashoffset, so the intro is the trajectory integrating
forward in time and the settled state is the attractor set it converged
onto. Nothing here is placed by hand: the picture is a consequence of
three lines of differential equation and a choice of viewpoint.

View: the rotation is chosen by search, not taste — of every orientation
on a 22.5-degree lattice this one projects widest (1.85:1), which is as
close as any system in genlib.SYSTEMS gets to filling a 12:5 frame.
`fit='height'` then runs the form to the edges instead of floating it
with margins.

Not Lorenz: it is the most reproduced object in generative art, and it
spirals too tightly for decimation to help (roughly 3x this file's path
data at the same tolerance).
"""
import genlib as G
from herolib import emit

SYSTEM = 'halvorsen'
ROTATION = (0.79, 2.36, 1.57)  # widest projection; see module docstring
PLANE, DEPTH = (0, 2), 1
TOL = 0.8   # decimation, in viewBox units — 23k points down to ~2.2k
NRUN = 150  # chronological runs; also the resolution of the draw-in

# Depth strata, far to near. Reusing one --px-* ramp for shading is the
# isometric hero's trick: every ramp has exactly three bands, so three
# strata need no new tokens and the closed set stays closed. The widths
# and colours live in the template — a run carries only its stratum
# class and its place in time.
STRATA = ('atr-far', 'atr-mid', 'atr-near')

pts = G.rotate(G.integrate(SYSTEM), *ROTATION)
screen, depth = G.project(pts, plane=PLANE, depth=DEPTH, fit='height')
runs = G.runs(screen, depth, G.decimate(screen, TOL), NRUN, len(STRATA))

# One subpath per element, because a dash pattern restarts at every
# subpath (see genlib.runs) — this is what makes the draw-in a trace
# rather than a fill. Everything paintable is a CSS concern; the only
# per-element data is the stratum and --i, which is ~80 bytes an element
# cheaper than spelling out stroke/width/cap/fill 150 times.
body = [f'  <path class="atr-run {STRATA[band]}" style="--i: {i}" '
        f'pathLength="1" d="{G.path_d([seg])}"/>'
        for band, seg, i in runs]

emit('atr-template.html', 'showcase/strange-attractor.html', '\n'.join(body))
