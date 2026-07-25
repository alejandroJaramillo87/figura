#!/usr/bin/env python3
"""Generate training-net sprites: 1 cell = 8 viewBox units, 150x62 canvas.
A small feedforward network — three sky input nodes, two steel hidden
layers of five and four, two green output nodes — joined by stepped pixel
wires. The layers snap in left to right; then an amber activation pulse
sweeps forward through the net, and a sky gradient pulse sweeps back —
one training step, forward and backward pass, on repeat. Single-pixel
glints twinkle on the node rims throughout."""
from herolib import emit, rect, rects

S = []

# 7x7 node sprites: outline ring, body lit from the upper left.
# Same shape, ramp swapped per layer.
NODE = [
    '..ooo..',
    '.o443o.',
    'o43332o',
    'o43322o',
    'o33221o',
    '.o221o.',
    '..ooo..',
]
NODE_SKY = [
    '..ooo..',
    '.okkSo.',
    'okSSSso',
    'okSSsso',
    'oSSssso',
    '.oSsso.',
    '..ooo..',
]
NODE_GRN = [
    '..ooo..',
    '.oeeGo.',
    'oeGGGgo',
    'oeGGggo',
    'oGGgggo',
    '.oGggo.',
    '..ooo..',
]
# amber-lit variant for the forward-pass pulse frames
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
IN = [(21, 15), (21, 31), (21, 47)]
H1 = [(56, 8), (56, 19), (56, 30), (56, 41), (56, 52)]
H2 = [(92, 12), (92, 25), (92, 38), (92, 51)]
OUT = [(127, 23), (127, 39)]

# drop a few edges per stage so no stage reads as a perfect grid
E1 = [(i, h) for i in range(3) for h in range(5)
      if (i, h) not in ((0, 4), (2, 0), (1, 2))]
E2 = [(a, b) for a in range(5) for b in range(4)
      if (a, b) not in ((0, 3), (4, 0), (2, 1))]
E3 = [(a, b) for a in range(4) for b in range(2) if (a, b) != (1, 1)]


def node(center, rows):
    cx, cy = center
    return rects(cx - 3, cy - 3, rows)


def edge_runs(a, b):
    """1-cell-thick 8-connected line between two node centers, clear of
    the sprites; cells merged into horizontal runs (x, y, w)."""
    (x1, y1), (x2, y2) = a, b
    x1, x2 = x1 + 4, x2 - 4
    n = max(x2 - x1, abs(y2 - y1))
    cells = []
    for i in range(n + 1):
        c = (x1 + round((x2 - x1) * i / n), y1 + round((y2 - y1) * i / n))
        if not cells or c != cells[-1]:
            cells.append(c)
    runs, (sx, sy) = [], cells[0]
    w = 1
    for x, y in cells[1:]:
        if y == sy:
            w += 1
        else:
            runs.append((sx, sy, w))
            sx, sy, w = x, y, 1
    runs.append((sx, sy, w))
    return runs


def edge(a, b, color, aa):
    """Staircase runs in `color`; on shallow steps (wide runs) a dimmer
    `aa` pixel softens the corner — pixel-art anti-aliasing. Steep
    zigzags stay bare: the 8-connected diagonal is already smooth."""
    runs = edge_runs(a, b)
    out = [rect(x, y, w, 1, color) for x, y, w in runs]
    for (px, py, pw), (nx, ny, nw) in zip(runs, runs[1:]):
        if pw >= 2 and nw >= 2:
            out.append(rect(nx, py, 1, 1, aa))   # extend prev row one dim cell

    return '\n'.join(out)


def stage(pairs, la, lb, color, aa):
    return '\n'.join(edge(la[i], lb[j], color, aa) for i, j in pairs)


# ============ structure: nodes and wires, layer by layer ============
def layer(cls, centers, rows):
    for i, ctr in enumerate(centers):
        S.append(f'  <g class="{cls}" style="--i: {i}">')
        S.append(node(ctr, rows))
        S.append('  </g>')


layer('tnet-in', IN, NODE_SKY)
S.append('  <g class="tnet-e1">')
S.append(stage(E1, IN, H1, '2', '1'))
S.append('  </g>')
layer('tnet-h1', H1, NODE)
S.append('  <g class="tnet-e2">')
S.append(stage(E2, H1, H2, '2', '1'))
S.append('  </g>')
layer('tnet-h2', H2, NODE)
S.append('  <g class="tnet-e3">')
S.append(stage(E3, H2, OUT, '2', '1'))
S.append('  </g>')
layer('tnet-out', OUT, NODE_GRN)

# ============ forward pass: 4 amber flipbook frames ============
S.append('  <g class="tnet-p1">')
for ctr in IN:
    S.append(node(ctr, NODE_LIT))
S.append(stage(E1, IN, H1, 'b', 'a'))
S.append('  </g>')

S.append('  <g class="tnet-p2">')
for ctr in H1:
    S.append(node(ctr, NODE_LIT))
S.append(stage(E2, H1, H2, 'b', 'a'))
S.append('  </g>')

S.append('  <g class="tnet-p3">')
for ctr in H2:
    S.append(node(ctr, NODE_LIT))
S.append(stage(E3, H2, OUT, 'b', 'a'))
S.append('  </g>')

S.append('  <g class="tnet-p4">')
for ctr in OUT:
    S.append(node(ctr, NODE_LIT))
S.append('  </g>')

# ============ backward pass: 3 sky edge-overlay frames ============
S.append('  <g class="tnet-b1">')
S.append(stage(E3, H2, OUT, 'S', 's'))
S.append('  </g>')
S.append('  <g class="tnet-b2">')
S.append(stage(E2, H1, H2, 'S', 's'))
S.append('  </g>')
S.append('  <g class="tnet-b3">')
S.append(stage(E1, IN, H1, 'S', 's'))
S.append('  </g>')

# ============ rim glints: 2 alternating scatter frames ============
G1 = [(IN[0], -2, -2), (IN[2], 2, -2), (H1[1], -2, 2), (H1[3], 2, -2),
      (H2[0], 2, 2), (H2[3], -2, -2), (OUT[1], 2, -2)]
G2 = [(IN[1], 2, 2), (H1[0], 2, -2), (H1[4], -2, -2), (H2[1], -2, 2),
      (H2[2], 2, -2), (OUT[0], -2, -2), (H1[2], 2, 2)]
for n, pts in ((1, G1), (2, G2)):
    S.append(f'  <g class="tnet-g{n}">')
    for (cx, cy), dx, dy in pts:
        S.append(rect(cx + dx, cy + dy, 1, 1, 'T', indent='    '))
    S.append('  </g>')

# ============ static dust for depth ============
for x, y in [(8, 6), (14, 56), (40, 3), (47, 59), (74, 4),
             (80, 58), (110, 5), (116, 57), (140, 8), (144, 50),
             (5, 34), (146, 30)]:
    S.append(rect(x, y, 1, 1, 'P'))

emit('tnet-template.html', 'sandboxing/training-net.html', '\n'.join(S))
