"""genlib — shared machinery for generative/algorithmic hero generators.

The third hero art style, alongside herolib (pixel art) and isolib
(isometric vector). Where those place marks by hand, this one computes
them and emits the result as <path> elements that CSS then draws.

Two families live here. Attractors are continuous and deterministic: a
dynamical system is integrated forward, projected and cut into runs.
Tilings are discrete and stochastic: a rule fires per cell and the
structure is whatever chains together. They share the emission end —
one component per element, one subpath per component — because that is
what makes a CSS reveal possible at all.

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
import random

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


# --- Tilings -------------------------------------------------------------
#
# The second family in this module. Where the attractors above are
# continuous and deterministic, these are discrete and stochastic, so they
# come with an invariant the ODEs did not need:
#
#   ALL RANDOMNESS GOES THROUGH A SEEDED random.Random, NEVER THE MODULE
#   FUNCTIONS.
#
# `npm run heroes` regenerates the whole library on every run and the
# validator diffs the result, so a generator that is not reproducible
# churns the working tree every time anyone touches an unrelated hero.
# Prefer .randrange()/.random() over .choice()/.shuffle(): those two have
# changed implementation across Python versions, the former have not.


def rng(seed):
    """The only sanctioned source of randomness in a generator."""
    return random.Random(seed)


def node_xy(key, tile):
    """Screen position of an edge midpoint. 'h' keys are the top edge of
    tile (i, j), 'v' keys its left edge."""
    kind, i, j = key
    return (((i + 0.5) * tile, j * tile) if kind == 'h'
            else (i * tile, (j + 0.5) * tile))


def tile_arcs(c, r, o, tile):
    """The two arcs of one Smith-Truchet tile in orientation o.

    Each arc is (node_a, node_b, cx, cy) and joins the midpoints of two
    adjacent edges, centred on the corner between them with radius
    tile/2. Orientation 0 pairs NW and SE, orientation 1 pairs NE and SW.
    Either way both arcs land on edge midpoints, so neighbouring tiles
    always connect -- that is the whole mechanism.
    """
    N, S = ('h', c, r), ('h', c, r + 1)
    W, E = ('v', c, r), ('v', c + 1, r)
    if o == 0:
        return [(N, W, c * tile, r * tile),
                (S, E, (c + 1) * tile, (r + 1) * tile)]
    return [(N, E, (c + 1) * tile, r * tile),
            (S, W, c * tile, (r + 1) * tile)]


def truchet_arcs(cols, rows, rnd, tile, skip=()):
    """Roll an orientation for every tile; emit arcs for the ones kept.

    Tiles in `skip` are rolled anyway and then dropped, so changing the
    skip set does not reshuffle the rest of the field. Their four edge
    midpoints become loose ends, which is what a generator wants when it
    means to leave some cells visibly undecided.
    """
    skip = set(skip)
    tiles, arcs = {}, []
    for r in range(rows):
        for c in range(cols):
            tiles[(c, r)] = rnd.randrange(2)
            if (c, r) not in skip:
                arcs += tile_arcs(c, r, tiles[(c, r)], tile)
    return tiles, arcs


def chain(arcs):
    """Walk an arc graph into components, each an ordered arc sequence.

    Every edge midpoint is shared by at most two tiles, so every node has
    degree <= 2 and this is a plain walk -- no union-find, no depth sort.
    Open runs are taken first, from the degree-1 nodes at the field
    boundary (and around any skipped tile); whatever is left is closed
    loops. That the loops exist at all is the point of the piece: nothing
    chose them, they fall out of one coin flip per tile.

    One component per <path> and one subpath per component, for the same
    reason `runs()` above cuts chronologically -- see its docstring.
    """
    adj = {}
    for i, (a, b, _cx, _cy) in enumerate(arcs):
        adj.setdefault(a, []).append(i)
        adj.setdefault(b, []).append(i)
    used, out = set(), []

    def walk(start):
        seq, cur = [], start
        while True:
            nxt = [i for i in adj[cur] if i not in used]
            if not nxt:
                return seq
            used.add(nxt[0])
            a, b, cx, cy = arcs[nxt[0]]
            end = b if a == cur else a
            seq.append((cur, end, cx, cy))
            cur = end

    for s in [n for n in adj if len(adj[n]) == 1] + list(adj):
        while any(i not in used for i in adj[s]):
            seq = walk(s)
            if seq:
                out.append(seq)
    return out


def arc_d(component, tile, radius):
    """One continuous subpath for a chained component.

    Every arc is a quarter circle, so large-arc is always 0; the sweep
    flag comes from the sign of (P-C) x (Q-C). SVG's y axis points down,
    so a positive cross product is the clockwise (sweep=1) direction.
    """
    x0, y0 = node_xy(component[0][0], tile)
    out = [f'M{round(x0)},{round(y0)}']
    for a, b, cx, cy in component:
        ax, ay = node_xy(a, tile)
        bx, by = node_xy(b, tile)
        sweep = 1 if (ax - cx) * (by - cy) - (ay - cy) * (bx - cx) > 0 else 0
        out.append(f'A{radius} {radius} 0 0 {sweep} {round(bx)},{round(by)}')
    return ' '.join(out)


# --- Layered graphs ------------------------------------------------------
#
# The third family. Attractors are continuous and deterministic, tilings
# discrete and stochastic; this one is stochastic and layered, and it
# exists to draw a network nobody placed.
#
# The point of sampling a net rather than drawing one is scale. A dozen
# hand-placed nodes joined by wires is diagram anatomy, and CLAUDE.md
# keeps that out of heroes. A hundred-odd sampled nodes under a falloff
# kernel is a texture that still reads as a network: too many to label,
# so it cannot explain anything, which is exactly what a hero wants.
#
# The same randomness invariant as the tilings applies -- everything goes
# through a seeded random.Random, or `npm run heroes` churns the tree.


def layers(counts, rnd, w=1200, h=500, pad=60, jitter=0.36, xjit=0.0):
    """Node positions for a feedforward stack, one list per layer.

    Layers sit at evenly spaced x. Within a layer the nodes spread over a
    band whose height is proportional to that layer's share of the widest
    one, so a tapering `counts` tapers the silhouette. Both axes are then
    jittered -- y by a fraction of the local spacing, x by `xjit` viewBox
    units -- which is what stops the columns reading as a ruled grid
    without stopping them reading as layers.
    """
    out, n, widest = [], len(counts), max(counts)
    for li, count in enumerate(counts):
        cx = pad + (w - 2 * pad) * (li / (n - 1) if n > 1 else 0.5)
        span = (h - 2 * pad) * (count / widest)
        step = span / max(count - 1, 1)
        top = (h - span) / 2
        col = []
        for k in range(count):
            x = cx + rnd.uniform(-xjit, xjit)
            y = top + k * step + rnd.uniform(-jitter, jitter) * step
            col.append((x, y))
        out.append(col)
    return out


def layer_edges(cols, rnd, sigma=52.0, kmax=4):
    """Edges between adjacent layers, sampled from a distance kernel.

    Each node offers an edge to every node in the next layer with
    probability exp(-dy^2 / 2 sigma^2). That Gaussian falloff is the
    whole art: what gets emitted is a sampled weight distribution rather
    than a drawn graph, so near connections dominate and the rare long
    one survives as a highlight.

    Two corrections keep the field readable. A node that draws no
    candidate is given its nearest forward neighbour, so nothing is
    stranded; and the accepted set is capped at kmax by a random key
    rather than by distance, which bounds density without quietly
    re-biasing the distribution back towards short edges.

    Returns (gap_index, (x0, y0), (x1, y1)) per edge.
    """
    out = []
    for li in range(len(cols) - 1):
        for x0, y0 in cols[li]:
            cand = []
            for x1, y1 in cols[li + 1]:
                dy = y1 - y0
                if rnd.random() < math.exp(-(dy * dy) / (2 * sigma * sigma)):
                    cand.append((rnd.random(), (x1, y1)))
            if not cand:
                cand = [(0.0, min(cols[li + 1], key=lambda q: abs(q[1] - y0)))]
            cand.sort(key=lambda t: t[0])
            for _k, q in cand[:kmax]:
                out.append((li, (x0, y0), q))
    return out
