#!/usr/bin/env python3
"""Generate motherboard-city sprites: 1 cell = 8 viewBox units, 150x62
canvas. Aerial pixel city at dusk — CPU heatsink downtown, RAM tower
blocks, VRM industrial district, trace-road streets. Power-on lights the
roads then each district; ambient headlights on the foreground avenue."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'diagrams', 'linux-ai-setup')
C = 8
COL = {
    'B': 'var(--bg)', 'P': 'var(--panel)', 'H': 'var(--panel-hover)',
    'M': 'var(--muted)', 'T': 'var(--text)',
    'V': 'var(--violet-dim)', 'v': 'var(--violet)', 'D': 'var(--accent-dim)',
    'E': 'var(--ok-dim)', 'w': 'var(--warn-dim)', 'R': 'var(--hot)',
    'L': 'var(--line)',
    'o': 'var(--px-outline)',
    '1': 'var(--px-steel-1)', '2': 'var(--px-steel-2)',
    '3': 'var(--px-steel-3)', '4': 'var(--px-steel-4)',
    'a': 'var(--px-amber-1)', 'b': 'var(--px-amber-2)', 'c': 'var(--px-amber-3)',
    'g': 'var(--px-green-1)', 'G': 'var(--px-green-2)', 'e': 'var(--px-green-3)',
    's': 'var(--px-sky-1)', 'S': 'var(--px-sky-2)', 'k': 'var(--px-sky-3)',
    'p': 'var(--px-dusk-1)', 'r': 'var(--px-dusk-2)', 'h': 'var(--px-dusk-3)',
}

def rects(ox, oy, rows, indent='    '):
    out = []
    for ry, row in enumerate(rows):
        x = 0
        while x < len(row):
            ch = row[x]
            if ch == '.':
                x += 1; continue
            x2 = x
            while x2 + 1 < len(row) and row[x2 + 1] == ch:
                x2 += 1
            out.append(f'{indent}<rect x="{(ox+x)*C}" y="{(oy+ry)*C}" '
                       f'width="{(x2-x+1)*C}" height="{C}" fill="{COL[ch]}"/>')
            x = x2 + 1
    return '\n'.join(out)

def rect(cx, cy, cw, ch_, color, cls='', style='', indent='    '):
    a = f' class="{cls}"' if cls else ''
    s = f' style="{style}"' if style else ''
    return (f'{indent}<rect{a}{s} x="{cx*C}" y="{cy*C}" width="{cw*C}" '
            f'height="{ch_*C}" fill="{COL[color]}"/>')

def dither_row(y, ch, phase=0):
    """2-cell checker blocks across the full width (chunky band edge)."""
    out = []
    x = phase * 2
    while x < 150:
        out.append(rect(x, y, 2, 1, ch))
        x += 4
    return '\n'.join(out)

S = []

# ============ sky (pop 0): banded dusk, stars, setting sun ============
S.append('  <g class="mbc-pop" style="--i: 0">')
S.append(dither_row(4, 'p'))                 # night -> plum
S.append(rect(0, 5, 150, 5, 'p'))            # plum band
S.append(rect(0, 10, 150, 1, 'p'))
S.append(dither_row(10, 'r', phase=1))       # plum -> rose
S.append(rect(0, 11, 150, 4, 'r'))           # rose band
S.append(rect(0, 15, 150, 1, 'r'))
S.append(dither_row(15, 'h'))                # rose -> peach
S.append(rect(0, 16, 150, 4, 'h'))           # peach horizon band
# stars only in the dark upper bands
for x, y in [(30, 2), (58, 1), (86, 3), (118, 2), (140, 5), (12, 6), (70, 7)]:
    S.append(rect(x, y, 1, 1, 'k'))
S.append(rect(100, 1, 1, 1, 'k', cls='mbc-twinkle'))
S.append(rect(46, 6, 1, 1, 'k', cls='mbc-twinkle'))
# setting sun, half-sunk on the horizon behind the harbor
S.append(rects(14, 15, [
    '..cccc..',
    '.cccccc.',
    'cccccccc',
    'cccccccc',
    'cccccccc',
]))
S.append('  </g>')

# ============ ground + harbor (pop 1) ============
S.append('  <g class="mbc-pop" style="--i: 1">')
S.append(rect(0, 20, 150, 1, 'o'))           # horizon / far board edge
S.append(rect(0, 21, 150, 37, '1'))          # PCB ground plane
S.append(rect(0, 58, 150, 4, 'o'))           # foreground falloff
# harbor water (I/O shield): stepped shoreline, sun-glint column
for wy, ww in [(21, 27), (22, 25), (23, 26), (24, 23), (25, 24), (26, 21)]:
    S.append(rect(0, wy, ww, 1, 'p'))
S.append(rect(0, 27, 26, 1, 'o'))            # quay edge
for gy in (21, 23, 25):                      # glint: dashed column under the sun
    S.append(rect(17, gy, 2, 1, 'c'))
S.append(rect(17, 26, 1, 1, 'h'))
# container ship at anchor, silhouetted on the water
S.append(rects(3, 22, [
    '.......o.',
    '.o.ooooo.',
    'ooooooooo',
    '.ooooooo.',
]))
S.append('  </g>')

# ============ back districts (pop 2): substation + VRM industrial ============
S.append('  <g class="mbc-pop" style="--i: 2">')
# substation (PSU): lattice pylon + transformer block
S.append(rects(2, 25, [
    'o...o',
    '.o.o.',
    'ooooo',
    '.o.o.',
    'o.o.o',
]))
S.append(rect(2, 30, 5, 4, 'o'))
S.append(rect(2, 30, 5, 1, '2'))             # dusk-lit top
S.append(rect(7, 34, 3, 1, 'o'))             # shadow right (sun from the west)
# container yard between quay and substation road
for i, (cx, cy) in enumerate([(10, 28), (13, 28), (17, 28), (10, 30),
                              (14, 30), (18, 30), (21, 28)]):
    S.append(rect(cx, cy, 3, 1, '2' if i % 2 else 'p'))
    S.append(rect(cx, cy + 1, 3, 1, 'o'))
# power flash overlay (the grid comes online)
S.append('    <g class="mbc-flash">')
S.append(rect(2, 29, 5, 1, 'k', indent='      '))
S.append(rect(3, 25, 3, 4, 'k', indent='      '))
S.append(rect(1, 30, 1, 3, 'S', indent='      '))
S.append(rect(7, 30, 1, 3, 'S', indent='      '))
S.append('    </g>')
# VRM chokes: four low blocks, dusk-lit roofs, dark windows
for i, bx in enumerate((10, 16, 22, 28)):
    S.append(rect(bx, 32, 4, 4, 'o'))
    S.append(rect(bx, 32, 4, 1, '2'))
    S.append(rect(bx + 1, 34, 1, 1, '1'))
    S.append(rect(bx + 2, 34, 1, 1, '1'))
    S.append(rect(bx + 4, 36, 2, 1, 'o'))    # shadow right
# capacitor tanks: two cylinders
for tx in (34, 38):
    S.append(rect(tx, 30, 3, 6, 'o'))
    S.append(rect(tx, 30, 3, 1, '2'))
    S.append(rect(tx, 31, 1, 4, 'p'))        # cool left shade
    S.append(rect(tx + 3, 36, 2, 1, 'o'))    # shadow right
S.append('  </g>')

# ============ skyline districts (pop 3): CPU downtown + RAM towers ============
S.append('  <g class="mbc-pop" style="--i: 3">')
# CPU heatsink fins = downtown towers (3w, 1 gap), tallest with antenna
downtown = [(56, 26), (60, 22), (64, 18), (68, 20), (72, 24), (76, 28), (80, 30)]
for tx, top in downtown:
    S.append(rect(tx, top, 3, 46 - top, 'o'))
    S.append(rect(tx, top, 3, 1, '2'))       # roof catches dusk
    if top <= 20:
        S.append(rect(tx, top + 1, 1, 6, 'p'))   # cool shade, tall faces
# antenna on the tallest fin
S.append(rect(65, 15, 1, 3, 'o'))
S.append(rect(65, 14, 1, 1, 'r'))
# dark window texture (static, unlit)
for tx, top in downtown:
    for wy in range(top + 3, 44, 3):
        S.append(rect(tx + 1, wy, 1, 1, '1'))
# IHS plaza slab at the towers' feet
S.append(rect(53, 46, 31, 1, '2'))
S.append(rect(53, 47, 31, 2, '1'))
S.append(rect(53, 49, 31, 1, 'o'))
# RAM: four identical tower slabs, roof boxes, dark floor windows
for rx in (96, 104, 112, 120):
    S.append(rect(rx, 24, 5, 20, 'o'))
    S.append(rect(rx, 24, 5, 1, '2'))
    S.append(rect(rx + 1, 23, 2, 1, 'o'))    # roof box
    S.append(rect(rx + 5, 44, 2, 1, 'o'))    # shadow right
    for wy in range(26, 43, 2):
        S.append(rect(rx + 1, wy, 1, 1, '1'))
        S.append(rect(rx + 3, wy, 1, 1, '1'))
S.append('  </g>')

# ============ foreground (pop 4): chipset, stadium, mall, avenue ============
S.append('  <g class="mbc-pop" style="--i: 4">')
# M.2 strip mall: long low block
S.append(rect(28, 46, 24, 4, 'o'))
S.append(rect(28, 46, 24, 1, '2'))
for dx in range(30, 51, 4):
    S.append(rect(dx, 48, 1, 1, '1'))
# coin-cell stadium: oval bowl with a dark field inside, sun-lit west rim
S.append(rects(85, 44, [
    '..oooooo..',
    '.oo1111oo.',
    'ho111111oo',
    'oo111111oo',
    '.oooooooo.',
]))
S.append(rect(94, 49, 2, 1, 'o'))            # shadow right
# chipset midtown: two blocks + beacon mast
S.append(rect(128, 40, 6, 10, 'o'))
S.append(rect(128, 40, 6, 1, '2'))
S.append(rect(137, 43, 6, 7, 'o'))
S.append(rect(137, 43, 6, 1, '2'))
for wy in (42, 45, 48):
    S.append(rect(130, wy, 1, 1, '1'))
    S.append(rect(132, wy, 1, 1, '1'))
for wy in (45, 47):
    S.append(rect(139, wy, 1, 1, '1'))
    S.append(rect(141, wy, 1, 1, '1'))
S.append(rect(129, 38, 1, 2, 'o'))           # beacon mast
S.append(rect(129, 37, 1, 1, 'R', cls='mbc-beacon'))
# trace roads (dark until energized): substation spine south then east
S.append(rect(6, 34, 1, 16, '2'))
S.append(rect(6, 50, 131, 1, '2'))
# stubs up to district doors (stay dark)
S.append(rect(30, 47, 1, 3, '2'))
S.append(rect(110, 44, 1, 6, '2'))
S.append(rect(131, 49, 1, 1, '2'))
# avenue: edges, roadbed, lane dashes
S.append(rect(0, 51, 150, 1, 'o'))
S.append(rect(0, 52, 150, 2, '2'))
S.append(rect(0, 54, 150, 1, 'o'))
# solder-pad ground texture in the open midground
for px, py in [(14, 40), (22, 44), (38, 41), (46, 44), (26, 47), (50, 43)]:
    S.append(rect(px, py, 2, 1, 'o'))
# far-right outskirts: radio mast + low warehouse
S.append(rect(145, 38, 1, 12, 'o'))
S.append(rect(146, 41, 2, 1, 'o'))
S.append(rect(144, 44, 2, 1, 'o'))
S.append(rect(145, 37, 1, 1, 'r'))
S.append(rect(141, 47, 6, 3, 'o'))
S.append(rect(141, 47, 6, 1, '2'))
for dx in range(2, 149, 6):
    S.append(rect(dx, 52, 2, 1, 'L', style='opacity:0.5'))
S.append('  </g>')

# ============ trace-road energize overlays (lit segments, sky blue) ============
seg_i = 0
S.append('  <g>')
for y0 in (34, 38, 42, 46):                  # vertical from the substation
    S.append(rect(6, y0, 1, 4, 'S', cls='mbc-road', style=f'--i: {seg_i}'))
    seg_i += 1
x0 = 7
while x0 < 137:                              # east along the spine
    w = min(10, 137 - x0)
    S.append(rect(x0, 50, w, 1, 'S', cls='mbc-road', style=f'--i: {seg_i}'))
    x0 += w; seg_i += 1
# district stubs light last, branching off the spine
S.append(rect(30, 47, 1, 3, 'S', cls='mbc-road', style=f'--i: {seg_i}'))
S.append(rect(110, 44, 1, 6, 'S', cls='mbc-road', style=f'--i: {seg_i}'))
S.append(rect(131, 49, 1, 1, 'S', cls='mbc-road', style=f'--i: {seg_i}'))
S.append('  </g>')

# ============ district light-up overlays (windows + ground glow) ============
def glow(cells, out, indent='      '):
    for x, y, wdt in cells:
        out.append(rect(x, y, wdt, 1, 'w', indent=indent))

# 0: VRM industrial
S.append('  <g class="mbc-lit" style="--i: 0">')
for bx in (10, 16, 22, 28):
    S.append(rect(bx + 1, 34, 1, 1, 'b', indent='      '))
    S.append(rect(bx + 2, 34, 1, 1, 'c', indent='      '))
glow([(10, 36, 4), (16, 36, 4), (22, 36, 4), (28, 36, 4), (34, 36, 3), (38, 36, 3)], S)
for tx in (34, 38):
    S.append(rect(tx + 1, 32, 1, 1, 'b', indent='      '))
S.append('  </g>')

# 1: CPU downtown
S.append('  <g class="mbc-lit" style="--i: 1">')
for tx, top in downtown:
    for j, wy in enumerate(range(top + 2, 44, 2)):
        ch = 'c' if (tx + wy) % 5 == 0 else 'b'
        S.append(rect(tx + 1, wy, 1, 1, ch, indent='      '))
glow([(54, 50, 32)], S)
S.append(rect(65, 14, 1, 1, 'R', cls='mbc-beacon', indent='      '))
S.append('  </g>')

# 2: RAM towers — frame glow; floors light via mbc-ram-row (bottom-up)
S.append('  <g class="mbc-lit" style="--i: 2">')
glow([(96, 44, 29)], S)
S.append('  </g>')
S.append('  <g>')
floors = list(range(42, 25, -2))             # y42 (bottom) .. y26 (top)
for i, wy in enumerate(floors):
    for rx in (96, 104, 112, 120):
        S.append(rect(rx + 1, wy, 1, 1, 'b', cls='mbc-ram-row',
                      style=f'--i: {i}', indent='    '))
        S.append(rect(rx + 3, wy, 1, 1, 'b', cls='mbc-ram-row',
                      style=f'--i: {i}', indent='    '))
S.append('  </g>')

# 3: chipset midtown + stadium
S.append('  <g class="mbc-lit" style="--i: 3">')
for wy in (42, 45, 48):
    S.append(rect(130, wy, 1, 1, 'b', indent='      '))
    S.append(rect(132, wy, 1, 1, 'c', indent='      '))
for wy in (45, 47):
    S.append(rect(139, wy, 1, 1, 'b', indent='      '))
S.append(rect(87, 45, 4, 1, 'b', indent='      '))   # stadium floodlit rim ring
S.append(rect(86, 46, 1, 1, 'b', indent='      '))
S.append(rect(92, 46, 1, 1, 'b', indent='      '))
S.append(rect(87, 47, 4, 1, 'w', indent='      '))   # field glow, dimmer
glow([(128, 50, 15), (85, 49, 10)], S)
S.append('  </g>')

# 4: M.2 mall + harbor lamps
S.append('  <g class="mbc-lit" style="--i: 4">')
for dx in range(30, 51, 4):
    S.append(rect(dx, 48, 1, 1, 'c', indent='      '))
glow([(28, 50, 24)], S)
S.append(rect(3, 26, 1, 1, 'c', indent='      '))    # crane lamp
S.append(rect(12, 27, 1, 1, 'c', indent='      '))   # quay lamp
S.append('  </g>')

# ============ ambient cars: 8-position headlight flipbook ============
S.append('  <g>')
for i in range(8):                            # car A: eastbound, upper lane
    S.append(rect(6 + i * 18, 52, 2, 1, 'c', cls=f'mbc-cp{i}'))
for j in range(8):                            # car B: westbound, lower lane
    S.append(rect(140 - j * 18, 53, 2, 1, 'R', cls=f'mbc-cp{(j + 4) % 8}'))
S.append('  </g>')

sprites = '\n'.join(S)
tpl = open(os.path.join(HERE, 'mbc-template.html')).read()
open(os.path.join(OUT, 'motherboard-city.html'), 'w').write(
    tpl.replace('@SPRITES@', sprites))
print(f'rects: {sprites.count("<rect")}')
