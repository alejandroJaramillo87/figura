"""genlib — shared machinery for generative/algorithmic hero generators.

The third hero art style, alongside herolib (pixel art) and isolib
(isometric vector). Where those place marks by hand, this one computes
them: a dynamical system is integrated forward, projected to the plane
and emitted as a handful of <path> elements that CSS then draws.

SYSTEMS below is canonical the way herolib.COL and isolib.RAMP are: a
new attractor is added here, never redefined in a generator. Everything
is stdlib — the repo has no Python dependencies and this module does not
introduce the first one.

Conventions: coordinates are rounded to whole viewBox units on the way
out (float noise is the biggest cause of bloated SVG output — see
isolib._poly), and trajectories are split into depth bands so the
projected tangle acquires light/dark massing instead of reading as one
flat scribble.
"""
import math

# Attractor ODEs. Each entry is (deriv, start, dt, steps) tuned so the
# orbit has settled onto the attractor and covered it evenly. `deriv`
# takes [x, y, z] and returns the derivative at that point.
SYSTEMS = {
    # Aizawa — a banded ellipsoid with an axial spike through it. Chosen
    # for the library's first generative hero because the silhouette is
    # specific enough to survive the thumbnail test, unlike the Lorenz
    # butterfly (which is also ~3x the path data: it spirals too tightly
    # for decimation to help).
    'aizawa': (
        lambda s: (
            (s[2] - 0.7) * s[0] - 3.5 * s[1],
            3.5 * s[0] + (s[2] - 0.7) * s[1],
            0.6 + 0.95 * s[2] - s[2] ** 3 / 3
            - (s[0] * s[0] + s[1] * s[1]) * (1 + 0.25 * s[2])
            + 0.1 * s[2] * s[0] ** 3,
        ),
        (0.1, 0.0, 0.0), 0.012, 26000,
    ),
    # Halvorsen — a three-lobed pinwheel with cyclic symmetry.
    'halvorsen': (
        lambda s: (
            -1.4 * s[0] - 4 * s[1] - 4 * s[2] - s[1] * s[1],
            -1.4 * s[1] - 4 * s[2] - 4 * s[0] - s[2] * s[2],
            -1.4 * s[2] - 4 * s[0] - 4 * s[1] - s[0] * s[0],
        ),
        (-5.0, 0.0, 0.0), 0.004, 26000,
    ),
    # Thomas — a cyclically symmetric lattice-like tangle.
    'thomas': (
        lambda s: (
            math.sin(s[1]) - 0.208186 * s[0],
            math.sin(s[2]) - 0.208186 * s[1],
            math.sin(s[0]) - 0.208186 * s[2],
        ),
        (1.0, 0.0, 1.0), 0.06, 26000,
    ),
    # Lorenz — the canonical one. Present for completeness; see the note
    # on 'aizawa' before reaching for it.
    'lorenz': (
        lambda s: (
            10 * (s[1] - s[0]),
            s[0] * (28 - s[2]) - s[1],
            s[0] * s[1] - 8 / 3 * s[2],
        ),
        (1.0, 1.0, 1.0), 0.008, 26000,
    ),
}


def integrate(name, warmup=0.1):
    """RK4-integrate a named system; drop the leading `warmup` fraction
    so the orbit has fallen onto the attractor before we draw it."""
    deriv, s, dt, n = SYSTEMS[name]
    pts = []
    for _ in range(n):
        k1 = deriv(s)
        k2 = deriv([s[i] + dt / 2 * k1[i] for i in range(3)])
        k3 = deriv([s[i] + dt / 2 * k2[i] for i in range(3)])
        k4 = deriv([s[i] + dt * k3[i] for i in range(3)])
        s = [s[i] + dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
             for i in range(3)]
        pts.append(s)
    return pts[int(n * warmup):]


def rotate(pts, ax=0.0, ay=0.0, az=0.0):
    """Rotate the trajectory in 3-space (radians, X then Y then Z) before
    projecting. Composition control: an attractor has no canonical
    viewpoint, so the view is chosen for silhouette and for how the form
    sits in a 12:5 frame."""
    ca, sa = math.cos(ax), math.sin(ax)
    cb, sb = math.cos(ay), math.sin(ay)
    cc, sc = math.cos(az), math.sin(az)
    out = []
    for x, y, z in pts:
        y, z = y * ca - z * sa, y * sa + z * ca
        x, z = x * cb + z * sb, -x * sb + z * cb
        x, y = x * cc - y * sc, x * sc + y * cc
        out.append((x, y, z))
    return out


def project(pts, plane=(0, 2), depth=1, fit='contain',
            w=1200, h=500, pad=30):
    """Project 3-space onto two of its axes, centred in the viewBox.
    Returns (screen_pts, depth_values).

    `fit` is the framing decision. These attractors are all roughly
    isotropic — the widest orientation of any system in SYSTEMS projects
    to about 1.85:1 against a 12:5 (2.4:1) frame — so something has to
    give: 'contain' leaves side margins, 'height' fills the frame
    vertically and lets the form run to the edges, 'width' fills
    horizontally and crops top and bottom. Aspect is always preserved;
    there is no stretch mode, because distorting a mathematical object
    to fit a frame is a lie about its shape.
    """
    a, b = plane
    us = [p[a] for p in pts]
    vs = [p[b] for p in pts]
    u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
    fw, fh = (w - 2 * pad) / (u1 - u0), (h - 2 * pad) / (v1 - v0)
    sc = {'contain': min(fw, fh), 'height': fh, 'width': fw}[fit]
    ox = (w - (u1 - u0) * sc) / 2 - u0 * sc
    oy = (h - (v1 - v0) * sc) / 2 - v0 * sc
    # v is flipped: SVG y grows downward, so the far side of the orbit
    # stays visually up.
    return ([(u * sc + ox, h - (v * sc + oy)) for u, v in zip(us, vs)],
            [p[depth] for p in pts])


def decimate(pts, tol):
    """Keep only the points a straight run would miss by more than `tol`
    viewBox units. Returns the kept indices.

    Iterative on purpose: a recursive Ramer-Douglas-Peucker blows
    Python's recursion limit on a 20k-point trajectory.
    """
    keep = [0]
    anchor = 0
    for i in range(2, len(pts)):
        ax, ay = pts[anchor]
        cx, cy = pts[i]
        dx, dy = cx - ax, cy - ay
        seg = math.hypot(dx, dy) or 1e-9
        for j in range(anchor + 1, i):
            px, py = pts[j]
            if abs(dx * (ay - py) - (ax - px) * dy) / seg > tol:
                keep.append(i - 1)
                anchor = i - 1
                break
    keep.append(len(pts) - 1)
    return keep


def runs(screen, depth, keep, nrun=150, nband=3):
    """Cut a decimated trajectory into `nrun` chronological runs, each
    tagged with the depth stratum it mostly occupies. Returns a list of
    (band_index, points, run_index).

    Chronological rather than by-depth, and that is the whole trick. A
    trajectory weaves front-to-back constantly, so grouping by depth
    would give a handful of paths made of a hundred disjoint subpaths
    each -- and an SVG dash pattern restarts at every subpath, so
    stroke-dashoffset on such a path does not trace it, it fills its
    runs in parallel from arbitrary offsets. One subpath per element is
    what makes a real draw-in possible; `run_index` then carries the
    chronology to CSS as --i, and each run takes the colour of the
    stratum it sits in, so depth still reads.
    """
    pts = [screen[i] for i in keep]
    dep = [depth[i] for i in keep]
    cuts = sorted(dep)
    edges = [cuts[len(cuts) * (i + 1) // nband] for i in range(nband - 1)]
    step = len(pts) / nrun
    out = []
    for r in range(nrun):
        a, b = int(r * step), int((r + 1) * step) + 1
        seg = pts[a:b]  # +1 so consecutive runs share an endpoint
        if len(seg) < 2:
            continue
        mid = dep[min((a + b) // 2, len(dep) - 1)]
        out.append((sum(1 for e in edges if mid > e), seg, r))
    return out


def path_d(subpaths):
    """`M x,y L …` for a list of subpaths, snapped to whole units."""
    out = []
    for sub in subpaths:
        if len(sub) < 2:
            continue
        pts = [f'{int(round(x))},{int(round(y))}' for x, y in sub]
        out.append('M ' + pts[0] + ' L ' + ' '.join(pts[1:]))
    return ' '.join(out)
