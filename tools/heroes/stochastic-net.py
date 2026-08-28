"""Stochastic net — a generative restatement of the training-net hero.

The pixel original places fourteen nodes by hand. This places none: seven
layers are sampled, and the edges between them are drawn from a Gaussian
falloff on y, so what is emitted is a sampled weight distribution rather
than a graph anyone laid out. At ~140 nodes the result stops being
diagram anatomy and becomes texture -- too many to label, which is what
keeps a hero a hero.

Emit order is paint order: the edge field first, then the nodes on top.
Two variables ride on each element. --i is the layer (or, for an edge,
the gap it spans) and drives the intro, which arrives one layer at a
time. --j is an edge's rank by midpoint x, and drives the ambient
sweep: ranking spatially rather than structurally turns the pulse into
a wavefront crossing the frame instead of a whole gap flashing at once,
which at ~90 edges per gap reads as a block rather than a pulse.
"""
import genlib as G
from herolib import emit

SEED = 3
COUNTS = (10, 21, 31, 29, 23, 16, 10)  # off-centre spindle: a form, not a slab
SIGMA, KMAX = 58.0, 4                  # kernel width, edges kept per node
XJIT = 26                              # softens the columns into bands

# Bands by how far an edge reaches -- the kernel made visible as tone.
BANDS = ((26, 'snet-e-tight'), (62, 'snet-e-mid'), (10 ** 9, 'snet-e-wide'))
STRATA = ('snet-in',) + ('snet-hidden',) * (len(COUNTS) - 2) + ('snet-out',)
RADII = (5.0,) + (4.0,) * (len(COUNTS) - 2) + (5.5,)

cols = G.layers(COUNTS, G.rng(SEED), pad=40, xjit=XJIT)
edges = G.layer_edges(cols, G.rng(SEED), sigma=SIGMA, kmax=KMAX)

# Rank by midpoint x. Ties broken by y so the ordering is total and the
# output is byte-stable across runs.
order = sorted(range(len(edges)),
               key=lambda n: ((edges[n][1][0] + edges[n][2][0]) / 2,
                              (edges[n][1][1] + edges[n][2][1]) / 2))
rank = {n: j for j, n in enumerate(order)}

body = []
for n, (g, p, q) in enumerate(edges):
    cls = next(c for lim, c in BANDS if abs(q[1] - p[1]) <= lim)
    body.append(f'  <path class="snet-edge {cls}" style="--i: {g}; --j: {rank[n]}" '
                f'pathLength="1" d="{G.path_d([[p, q]])}"/>')

for li, col in enumerate(cols):
    for x, y in col:
        body.append(f'  <circle class="snet-node {STRATA[li]}" '
                    f'style="--i: {li}" cx="{x:.1f}" cy="{y:.1f}" '
                    f'r="{RADII[li]}"/>')

print(f'edges: {len(edges)}, nodes: {sum(len(c) for c in cols)}')
emit('snet-template.html', 'showcase/stochastic-net.html', '\n'.join(body))
