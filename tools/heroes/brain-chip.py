#!/usr/bin/env python3
"""Generate brain-chip sprites: 1 cell = 8 viewBox units, 150x62 canvas.
One large frontal chip package holding a pixel brain — the sealed mind of
an inference appliance. A green trace loops out of one east pin and back
into its neighbor (loopback-only networking); a hot dashed inbound
attempt from the left bursts against the package wall and gets nowhere."""
from herolib import emit, rect, rects

S = []

PX, PY = 55, 11         # package top-left: 40x40 package centered

# ============ package body + pins (pop 0) ============
S.append('  <g class="bch-pop" style="--i: 0">')

# pins: 5 per side, steel; the two live east pins are drawn in bch-loop
for i in range(5):
    off = PX + 4 + i * 8
    S.append(rect(off, PY - 4, 2, 4, '3'))            # north
    S.append(rect(off, PY + 40, 2, 4, '3'))           # south
    offy = PY + 4 + i * 8
    S.append(rect(PX - 4, offy, 4, 2, '3'))           # west
    if i not in (1, 2):
        S.append(rect(PX + 40, offy, 4, 2, '3'))      # east minus live pair

# package: steel fill, warm top highlight, cool bottom/right shadow
S.append(rect(PX + 1, PY + 1, 38, 38, '2'))
S.append(rect(PX + 1, PY + 1, 38, 2, '4'))
S.append(rect(PX + 1, PY + 37, 38, 2, '1'))
S.append(rect(PX + 1, PY + 3, 2, 34, '3'))
S.append(rect(PX + 37, PY + 3, 2, 34, '1'))
# outline
S.append(rect(PX, PY, 40, 1, 'o'))
S.append(rect(PX, PY + 39, 40, 1, 'o'))
S.append(rect(PX, PY + 1, 1, 38, 'o'))
S.append(rect(PX + 39, PY + 1, 1, 38, 'o'))
# inner die frame + cavity
S.append(rect(PX + 4, PY + 4, 32, 1, 'o'))
S.append(rect(PX + 4, PY + 35, 32, 1, 'o'))
S.append(rect(PX + 4, PY + 5, 1, 30, 'o'))
S.append(rect(PX + 35, PY + 5, 1, 30, 'o'))
S.append(rect(PX + 5, PY + 5, 30, 30, '1'))
S.append('  </g>')

# ============ brain hemispheres (hard-cut reveals) ============
# 13-wide maps per hemisphere in the 30x30 cavity, midline gap between.
# Y = violet mid, y = violet-1 fold shadows, z = violet-3 highlight.
BX, BY = PX + 6, PY + 10
LHEMI = [
    '.......YYYYYY',
    '....YYYzzYYYY',
    '..YYYyyYYYYYY',
    '.YYYYYYYYyyYY',
    'YYyyYYYYYYYYY',
    'YYYYYYyyyYYYY',
    'YYYYYYYYYYYyY',
    'YYyyyYYYYYYYY',
    'YYYYYYYyyYYYY',
    'YYYYYYYYYYYYY',
    'YyyYYYYYYyyYY',
    'YYYYYyyYYYYYY',
    'YYYYYYYYYYYYY',
    '.YYyyYYYYyyYY',
    '.YYYYYYYYYYYY',
    '..YYYYyyYYYYY',
    '..YYYYYYYYYYY',
    '...YYyyYYYYYY',
    '....YyYYYYYYY',
    '......YYYYYYY',
]
RHEMI = [
    'YzzYYY.......',
    'zYYYzYYYY....',
    'YYYYyyYYYY...',
    'YYyyYYYYYYY..',
    'YYYYYYYyyYYY.',
    'YYYYyyYYYYYY.',
    'YyYYYYYYYYYYY',
    'YYYYYYyyYYYYY',
    'YYYyyYYYYYYYY',
    'YYYYYYYYYyyYY',
    'YYyyYYYYYYYYY',
    'YYYYYYyyYYYYY',
    'YYYYYYYYYYYyy',
    'YYyyYYYYyyYY.',
    'YYYYYYYYYYYY.',
    'YYYYyyYYYYY..',
    'YYYYYYYYYYY..',
    'YYYYYyyYYY...',
    'YYYYYYYyy....',
    'YYYYYYY......',
]
S.append('  <g class="bch-hemi bch-hemi-l">')
S.append(rects(BX, BY, LHEMI))
S.append('  </g>')
S.append('  <g class="bch-hemi bch-hemi-r">')
S.append(rects(BX + 14, BY, RHEMI))
S.append('  </g>')

# ============ synapse sparkle: 2 flipbook frames ============
SYN1 = [(4, 5, 'k'), (9, 2, 'z'), (17, 4, 'z'), (22, 9, 'k'),
        (6, 12, 'z'), (12, 8, 'k'), (19, 14, 'z'), (9, 17, 'k')]
SYN2 = [(7, 3, 'z'), (14, 5, 'k'), (20, 2, 'z'), (3, 9, 'k'),
        (11, 13, 'z'), (23, 12, 'z'), (16, 17, 'k'), (5, 16, 'z')]
for n, pts in ((1, SYN1), (2, SYN2)):
    S.append(f'  <g class="bch-syn bch-syn-{n}">')
    for x, y, c in pts:
        S.append(rect(BX + x, BY + y, 1, 1, c, indent='    '))
    S.append('  </g>')

# ============ loopback: live east pins + trace (snap-on) ============
Y1 = PY + 4 + 1 * 8
Y2 = PY + 4 + 2 * 8
S.append('  <g class="bch-loop">')
S.append(rect(PX + 40, Y1, 4, 2, 'G', indent='    '))   # live pin out
S.append(rect(PX + 40, Y2, 4, 2, 'G', indent='    '))   # live pin in
S.append(rect(PX + 44, Y1, 14, 2, 'g', indent='    '))  # trace out
S.append(rect(PX + 56, Y1, 2, Y2 - Y1 + 2, 'g', indent='    '))
S.append(rect(PX + 44, Y2, 14, 2, 'g', indent='    '))  # trace back
S.append('  </g>')

# flow pixels marching around the loop: 2 flipbook frames
FLOW1 = [(PX + 47, Y1), (PX + 53, Y1), (PX + 56, Y1 + 4),
         (PX + 52, Y2 + 1), (PX + 46, Y2 + 1)]
FLOW2 = [(PX + 50, Y1), (PX + 56, Y1 + 1), (PX + 56, Y2 - 1),
         (PX + 49, Y2 + 1), (PX + 44, Y2 + 1)]
for n, pts in ((1, FLOW1), (2, FLOW2)):
    S.append(f'  <g class="bch-flow bch-flow-{n}">')
    for x, y in pts:
        S.append(rect(x, y, 1, 1, 'G', indent='    '))
    S.append('  </g>')

# ============ blocked inbound: 2 drawn frames + implicit empty ======
YB = PY + 20
S.append('  <g class="bch-in bch-in-1">')
for x in range(14, 34, 4):
    S.append(rect(x, YB, 2, 2, 'x', indent='    '))
S.append(rect(22, YB, 2, 2, 'X', indent='    '))
S.append('  </g>')
S.append('  <g class="bch-in bch-in-2">')
for x in range(22, 42, 4):
    S.append(rect(x, YB, 2, 2, 'x', indent='    '))
S.append(rect(34, YB, 2, 2, 'X', indent='    '))
for x, y in [(PX - 6, YB - 2), (PX - 7, YB), (PX - 6, YB + 3),
             (PX - 9, YB + 1), (PX - 8, YB - 1)]:
    S.append(rect(x, y, 1, 1, 'X', indent='    '))
S.append(rect(PX - 7, YB + 1, 1, 1, 'Z', indent='    '))
S.append('  </g>')

# ============ static dust for depth ============
for x, y in [(18, 8), (30, 46), (122, 12), (135, 40), (46, 4),
             (105, 54), (10, 28), (141, 24), (95, 6), (62, 58)]:
    S.append(rect(x, y, 1, 1, 'P'))

emit('bch-template.html', 'sandboxing/brain-chip.html', '\n'.join(S))
