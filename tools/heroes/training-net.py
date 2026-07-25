#!/usr/bin/env python3
"""Generate training-net sprites: 1 cell = 8 viewBox units, 150x62 canvas.
A small feedforward network — three input nodes, four hidden, two output —
drawn as chunky steel pixel spheres joined by stepped pixel wires. The
layers snap in left to right; then an amber activation pulse sweeps
through the net layer by layer, a forward pass on repeat."""
from herolib import emit, rect, rects

S = []

# 7x7 node sprite: outline ring, steel body lit from the upper left
NODE = [
    '..ooo..',
    '.o443o.',
    'o43332o',
    'o43322o',
    'o33221o',
    '.o221o.',
    '..ooo..',
]
# amber-lit variant for the activation pulse frames
NODE_LIT = [
    '..ooo..',
    '.occbo.',
    'occbbbo',
    'ocbbbao',
    'obbbaao',
    '.obaao.',
    '..ooo..',
]

# node centers in cell coordinates (cx, cy)
IN = [(28, 15), (28, 31), (28, 47)]
HID = [(73, 10), (73, 24), (73, 38), (73, 52)]
OUT = [(118, 23), (118, 39)]

# drop a few edges so the mesh does not read as a perfect grid
E1 = [(i, h) for i in range(3) for h in range(4) if (i, h) not in ((0, 3), (2, 0))]
E2 = [(h, o) for h in range(4) for o in range(2) if (h, o) != (0, 1)]


def node(center, rows):
    cx, cy = center
    return rects(cx - 3, cy - 3, rows)


def edge_runs(a, b):
    """1-cell-thick staircase between two node centers, clear of the
    sprites; returns horizontal runs (x, y, w)."""
    (x1, y1), (x2, y2) = a, b
    x1, x2 = x1 + 4, x2 - 4
    n = x2 - x1
    pts = [(x1 + i, round(y1 + (y2 - y1) * i / n)) for i in range(n + 1)]
    runs, (sx, sy) = [], pts[0]
    for x, y in pts[1:]:
        if y != sy:
            runs.append((sx, sy, x - sx))
            sx, sy = x, y
    runs.append((sx, sy, pts[-1][0] - sx + 1))
    return runs


def edge(a, b, color):
    return '\n'.join(rect(x, y, w, 1, color) for x, y, w in edge_runs(a, b))


# ============ structure: nodes and wires, layer by layer ============
for i, ctr in enumerate(IN):
    S.append(f'  <g class="tnet-in" style="--i: {i}">')
    S.append(node(ctr, NODE))
    S.append('  </g>')

S.append('  <g class="tnet-e1">')
for i, h in E1:
    S.append(edge(IN[i], HID[h], '2'))
S.append('  </g>')

for i, ctr in enumerate(HID):
    S.append(f'  <g class="tnet-hid" style="--i: {i}">')
    S.append(node(ctr, NODE))
    S.append('  </g>')

S.append('  <g class="tnet-e2">')
for h, o in E2:
    S.append(edge(HID[h], OUT[o], '2'))
S.append('  </g>')

for i, ctr in enumerate(OUT):
    S.append(f'  <g class="tnet-out" style="--i: {i}">')
    S.append(node(ctr, NODE))
    S.append('  </g>')

# ============ forward-pass pulse: 3 flipbook frames ============
# p1: inputs fire and the first wire stage carries the signal
S.append('  <g class="tnet-p1">')
for ctr in IN:
    S.append(node(ctr, NODE_LIT))
for i, h in E1:
    S.append(edge(IN[i], HID[h], 'b'))
S.append('  </g>')

# p2: hidden layer fires, second wire stage carries
S.append('  <g class="tnet-p2">')
for ctr in HID:
    S.append(node(ctr, NODE_LIT))
for h, o in E2:
    S.append(edge(HID[h], OUT[o], 'b'))
S.append('  </g>')

# p3: outputs light up
S.append('  <g class="tnet-p3">')
for ctr in OUT:
    S.append(node(ctr, NODE_LIT))
S.append('  </g>')

# ============ static dust for depth ============
for x, y in [(10, 6), (18, 56), (48, 3), (57, 59), (94, 5),
             (102, 57), (136, 8), (143, 52), (7, 36), (140, 30)]:
    S.append(rect(x, y, 1, 1, 'P'))

emit('tnet-template.html', 'sandboxing/training-net.html', '\n'.join(S))
