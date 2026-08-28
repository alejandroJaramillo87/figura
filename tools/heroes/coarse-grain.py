#!/usr/bin/env python3
"""Generate coarse-grain: memory as an isometric plain, tiled two ways."""
import genlib as G
import isolib as I
from herolib import emit
from isolib import prism, project

I.S = 44
OX, OY = 600.0, -200.0
W, H = 1200, 500
MARGIN = 24
PLAIN = 22
OVER = 10          # emit past the plain's nominal edges; the rhombus
                   # corners would otherwise leave the frame's corners bare
SEED = 5
HOT_P = 0.10
POOL_X, POOL_Z, POOL_N, SLAB = 6, 10, 2, 3
GAP = 0.16          # keeps adjacent reserved slabs from merging into one shape

# Weighted so the plain reads as one lit surface with variation, not as
# static: mostly the mid band, a few darker cells, the odd highlight.
MOTTLE = ('0',) * 14 + ('d', '1')

rnd = G.rng(SEED)
P = []


def visible(x, z, w=1, d=1):
    pts = [project(x + dx, 0, z + dz, OX, OY)
           for dx, dz in ((0, 0), (w, 0), (w, d), (0, d))]
    return (min(p[0] for p in pts) < W + MARGIN
            and max(p[0] for p in pts) > -MARGIN
            and min(p[1] for p in pts) < H + MARGIN
            and max(p[1] for p in pts) > -MARGIN)


cells = []
for x in range(-OVER, PLAIN + OVER):
    for z in range(-OVER, PLAIN + OVER):
        # The floor runs under the reserved block too: the slabs stand
        # proud of it, so cutting the floor away would show panel
        # background behind their raised back edges.
        if not visible(x, z):
            continue
        ch = 'x' if rnd.random() < HOT_P else MOTTLE[rnd.randrange(len(MOTTLE))]
        cells.append((x, z, ch))

# --i is depth along the isometric axis, normalised to start at 0. It
# drives the back-to-front intro and, in the settled state, a ripple
# travelling the same axis -- one variable, two readings.
BASE = min(x + z for x, z, _ in cells)

for x, z, ch in sorted(cells, key=lambda c: c[0] + c[1]):
    # Hot cells stand slightly proud, so pressure has relief as well as
    # colour; the calm field stays one polygon per cell.
    if ch == 'x':
        P.append(prism(x, 0, z, 1, 0.22, 1, 'x', ox=OX, oy=OY,
                       cls='cgr-hot', style=f'--i: {x + z - BASE}'))
    else:
        P.append(prism(x, 0, z, 1, 1, 1, ch, only='t', ox=OX, oy=OY,
                       cls='cgr-fine', style=f'--i: {x + z - BASE}'))

slabs = [(POOL_X + sx * SLAB, POOL_Z + sz * SLAB)
         for sx in range(POOL_N) for sz in range(POOL_N)]
for x, z in sorted(slabs, key=lambda c: c[0] + c[1]):
    P.append(prism(x + GAP, 0, z + GAP, SLAB - 2 * GAP, 0.75, SLAB - 2 * GAP,
                   'g', ox=OX, oy=OY, cls='cgr-slab', style=f'--i: {x + z - BASE}'))

print(f'fine: {len(cells)}, slabs: {len(slabs)}, depth span: {max(x + z for x, z, _ in cells) - BASE}')
emit('cgr-template.html', 'showcase/coarse-grain.html', '\n'.join(P))
