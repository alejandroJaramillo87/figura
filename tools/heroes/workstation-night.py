#!/usr/bin/env python3
"""Generate workstation-night sprites: 1 cell = 8 viewBox units, 150x62
canvas. Night scene — the monitor is the light source; a boot flipbook
drives a color-changing glow spill over desk, wall and floor. Window with
rain, moon, and a city skyline. Steel ramp 1..4; selective outlines 'o'."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'diagrams', 'linux-ai-setup')
C = 8
COL = {
    'B': 'var(--bg)', 'P': 'var(--panel)', 'H': 'var(--panel-hover)',
    'M': 'var(--muted)', 'T': 'var(--text)',
    'V': 'var(--violet-dim)', 'v': 'var(--violet)', 'D': 'var(--accent-dim)',
    'E': 'var(--ok-dim)', 'w': 'var(--warn-dim)',
    'L': 'var(--line)',
    'o': 'var(--px-outline)',
    '1': 'var(--px-steel-1)', '2': 'var(--px-steel-2)',
    '3': 'var(--px-steel-3)', '4': 'var(--px-steel-4)',
    'a': 'var(--px-amber-1)', 'b': 'var(--px-amber-2)', 'c': 'var(--px-amber-3)',
    'g': 'var(--px-green-1)', 'G': 'var(--px-green-2)', 'e': 'var(--px-green-3)',
    's': 'var(--px-sky-1)', 'S': 'var(--px-sky-2)', 'k': 'var(--px-sky-3)',
    'p': 'var(--px-dusk-1)', 'r': 'var(--px-dusk-2)', 'h': 'var(--px-dusk-3)',
}

def dither(ox, y, w, ch, phase=0):
    # 2-cell checker blocks every 4 cells — band-transition dither
    return '\n'.join(rect(x, y, 2, 1, ch)
                     for x in range(ox + phase * 2, ox + w - 1, 4))

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

S = []

# ============ room shell (pop 0): floor + window wall ============
S.append('  <g class="wsn-pop" style="--i: 0">')
# floor: darker than the wall (--bg panel background); boundary line
S.append(rect(0, 56, 150, 1, '1'))
S.append(rect(0, 57, 150, 5, 'o'))
# window: outer frame x10..45, y5..28; mullions; night sky interior stays --bg
S.append(rect(10, 5, 36, 1, '1'))    # frame top
S.append(rect(10, 28, 36, 1, '1'))   # frame bottom
S.append(rect(10, 6, 1, 22, '1'))    # frame left
S.append(rect(45, 6, 1, 22, '1'))    # frame right
# dusk sky bands behind the skyline: plum -> rose -> peach horizon,
# with checker-dither transition rows (mullions/skyline paint on top)
# plum dominates so the window never outshines the monitor; peach is a
# 2-row horizon sliver that only glints between the building silhouettes
S.append(rect(11, 6, 34, 10, 'p'))   # plum, y6-15
S.append(dither(11, 15, 34, 'r'))
S.append(rect(11, 16, 34, 5, 'r'))   # dusty rose, y16-20
S.append(dither(11, 20, 34, 'h', phase=1))
S.append(rect(11, 21, 34, 2, 'h'))   # peach horizon sliver, y21-22
# dusk light bleeds past the frame onto the wall: 1-cell dithered fringe
S.append(dither(10, 4, 36, 'p'))
S.append(dither(9, 30, 38, 'p', phase=1))
for fy in range(7, 27, 4):
    S.append(rect(9, fy, 1, 1, 'p'))
    S.append(rect(46, fy + 2, 1, 1, 'p'))
S.append(rect(27, 6, 1, 22, '1'))    # vertical mullion
S.append(rect(11, 16, 34, 1, '1'))   # horizontal mullion
# window sill (slightly lit — moonlight)
S.append(rect(9, 29, 38, 1, '2'))
# moon: stepped pale disc with a shaded lower-right terminator limb
S.append(rects(36, 7, [
    '.kkk.',
    'kkkkk',
    'kkkk4',
    'kkk44',
    '.k44.',
]))
# stars (static)
for x, y in [(14, 8), (20, 11), (31, 7), (34, 13)]:
    S.append(rect(x, y, 1, 1, 'k'))
# twinkling stars + one twinkling city window share the ambient class
S.append(rect(24, 9, 1, 1, 'k', cls='wsn-twinkle'))
S.append(rect(17, 14, 1, 1, 'k', cls='wsn-twinkle'))
# city skyline: blocky stepped buildings (darker than the sky), a thin
# antenna, windows aligned in columns inside the tall blocks
S.append(rects(11, 17, [
    '.............o..................',
    '....oooo.....o.........ooo......',
    '....oooo.....o.........ooo......',
    '....oooo...ooooo..oooo.ooo......',
    'ooo.oooo...ooooo..oooo.ooo.ooooo',
    'ooo.oooo...ooooo..oooo.ooo.ooooo',
    'oooooooooooooooooooooooooooooooo',
    'oooooooooooooooooooooooooooooooo',
    'oooooooooooooooooooooooooooooooo',
    'oooooooooooooooooooooooooooooooo',
    'oooooooooooooooooooooooooooooooo',
]))
# lit city windows light up in a stagger ladder during the intro;
# far/low windows sit in a recessed 0.5-alpha group for depth
for i, (x, y) in enumerate([(16, 19), (16, 21), (23, 21), (34, 21)]):
    S.append(rect(x, y, 1, 1, 'a', cls='wsn-city-win', style=f'--i: {i}'))
S.append('    <g style="opacity:0.5">')
for i, (x, y) in enumerate([(12, 22), (39, 22)], start=4):
    S.append(rect(x, y, 1, 1, 'a', cls='wsn-city-win', style=f'--i: {i}',
                  indent='      '))
S.append('    </g>')
S.append(rect(25, 22, 1, 1, 'b', cls='wsn-city-win wsn-twinkle', style='--i: 6'))
# rain: two alternating flipbook frames of 1x2 streaks inside the panes
S.append('    <g class="wsn-rain wsn-rain-1">')
for x, y in [(13, 8), (18, 12), (23, 7), (16, 19), (21, 22), (12, 24),
             (30, 9), (35, 13), (40, 8), (32, 20), (38, 23), (43, 18)]:
    S.append(rect(x, y, 1, 2, 's', indent='      '))
# far rain layer: shorter 1x1 streaks recessed at half alpha (depth)
for x, y in [(15, 9), (26, 14), (12, 18), (33, 8), (42, 15), (29, 23)]:
    S.append(rect(x, y, 1, 1, 's', style='opacity:0.5', indent='      '))
S.append('    </g>')
S.append('    <g class="wsn-rain wsn-rain-2">')
for x, y in [(15, 11), (20, 15), (25, 10), (14, 22), (19, 25), (24, 20),
             (28, 12), (33, 17), (38, 11), (30, 24), (36, 25), (41, 21)]:
    S.append(rect(x, y, 1, 2, 's', indent='      '))
for x, y in [(17, 7), (22, 18), (13, 13), (36, 9), (44, 20), (31, 25)]:
    S.append(rect(x, y, 1, 1, 's', style='opacity:0.5', indent='      '))
S.append('    </g>')
S.append('  </g>')

# ============ desk (pop 1) — dark shades, the spill lights it ============
S.append('  <g class="wsn-pop" style="--i: 1">')
S.append(rect(76, 26, 52, 1, '2'))    # tabletop (dark)
S.append(rect(76, 27, 52, 1, 'o'))    # front edge shadow
S.append(rect(78, 28, 2, 28, '1'))    # left leg
S.append(rect(124, 28, 2, 28, '1'))   # right leg
S.append(rect(77, 56, 4, 1, 'o'))     # contact shadows
S.append(rect(123, 56, 4, 1, 'o'))
S.append('  </g>')

# ============ set dressing (also pop 1): plant, poster, cable ============
S.append('  <g class="wsn-pop" style="--i: 1">')
# floor plant left of the tower, dark silhouette with faint leaf shades
S.append(rects(44, 47, [
    '..g.g..',
    '.g1g1g.',
    '..1g1..',
    '..o1o..',
    '..111..',
    '..111..',
]))
S.append(rect(45, 53, 3, 3, '1'))     # pot
S.append(rect(44, 56, 5, 1, 'o'))     # contact shadow
# dim poster on the right wall, art barely visible in the dark
S.append(rects(132, 8, [
    'ooooooooooo',
    'o111111111o',
    'o112111111o',
    'o121211121o',
    'o111112121o',
    'o111121111o',
    'o111111111o',
    'ooooooooooo',
]))
# power cable from tower to a wall socket
S.append(rect(50, 54, 5, 1, 'o'))
S.append(rect(50, 52, 1, 2, 'o'))
S.append(rect(49, 51, 2, 1, '1'))     # socket plate
S.append('  </g>')

# ============ tower (pop 2) — dark at night ============
S.append('  <g class="wsn-pop" style="--i: 2">')
# cool shadow side ('p', dusk-1) on the column away from the window
tower = ['ooooooooooooooooooo',
         'o2222222222222221po'] + \
        ['o2111111111111111po'] * 24 + \
        ['o1111111111111111po',
         'ooooooooooooooooooo']
S.append(rects(55, 28, tower))
# fan: outlined ring, recessed dark well
fan_ring = [
    '..ooooooo..',
    '.o1111111o.',
    'o111111111o',
    'o111111111o',
    'o111111111o',
    'o111111111o',
    'o111111111o',
    'o111111111o',
    'o111111111o',
    '.o1111111o.',
    '..ooooooo..',
]
S.append(rects(59, 36, fan_ring))
S.append(rect(64, 41, 1, 1, '2'))     # hub
S.append('    <g class="wsn-fan wsn-fan-1">')     # plus
S.append(rects(61, 38, [
    '...3...',
    '...3...',
    '...3...',
    '333.333',
    '...3...',
    '...3...',
    '...3...',
], indent='      '))
S.append('    </g>')
S.append('    <g class="wsn-fan wsn-fan-2">')     # pinwheel cw
S.append(rects(61, 38, [
    '....3..',
    '....3..',
    '...33..',
    '33...33',
    '..33...',
    '..3....',
    '..3....',
], indent='      '))
S.append('    </g>')
S.append('    <g class="wsn-fan wsn-fan-3">')     # x
S.append(rects(61, 38, [
    '3.....3',
    '.3...3.',
    '..3.3..',
    '.......',
    '..3.3..',
    '.3...3.',
    '3.....3',
], indent='      '))
S.append('    </g>')
S.append('    <g class="wsn-fan wsn-fan-4">')     # pinwheel ccw
S.append(rects(61, 38, [
    '..3....',
    '..3....',
    '..33...',
    '33...33',
    '...33..',
    '....3..',
    '....3..',
], indent='      '))
S.append('    </g>')
for vy in (49, 51, 53):
    S.append(rect(59, vy, 11, 1, 'o'))
S.append(rect(54, 33, 1, 2, '2'))     # power button (dark until wake)
S.append('    <g class="wsn-led">')
S.append(rect(58, 30, 1, 1, 'G', indent='      '))
S.append(rect(57, 30, 1, 1, 'g', indent='      '))
S.append('    </g>')
S.append(rect(55, 56, 20, 1, 'o'))    # contact shadow (floor is 'o' too; keep)
S.append('  </g>')

# ============ monitor (pop 3) with screen scenes ============
S.append('  <g class="wsn-pop" style="--i: 3">')
# monitor bezel: warm '2' top face, cool 'p' shadow column on the right
mon = ['oooooooooooooooooooooooooooooooo',
       'o22222222222222222222222222221po'] + \
      ['o2' + 'B' * 27 + 'po'] * 16 + \
      ['o21111111111111111111111111111po',
       'oooooooooooooooooooooooooooooooo']
S.append(rects(86, 4, mon))
S.append(rect(100, 24, 3, 1, '1'))            # stand
S.append(rect(96, 25, 11, 1, '1'))            # base top
S.append(rect(96, 26, 11, 1, 'o'))            # base shadow
# dark keyboard, mouse, mug (silhouettes; the spill lights them)
S.append(rect(88, 25, 14, 1, '1'))
S.append(rect(87, 26, 16, 1, 'o'))
S.append(rect(108, 25, 2, 1, '1'))
# mug sits clear of the glow-spill wall halo (x118-119) and desk-wash
# dither so the spill never paints over it
S.append(rect(122, 23, 3, 1, 'b'))            # mug rim catches screen light
S.append(rect(122, 24, 3, 2, 'a'))            # mug body (dark amber)
S.append(rect(125, 24, 1, 1, 'a'))            # handle
S.append(rect(121, 26, 5, 1, 'o'))            # mug shadow on tabletop
# screen region: x 88..114 (27 wide), y 6..20 (15 tall)
SX, SY, SW, SH = 88, 6, 27, 15
S.append('    <g class="wsn-scene-off">')
S.append(rect(SX, SY, SW, SH, 'B', indent='      '))
for i in range(4):                              # off-glass diagonal glint
    S.append(rect(SX + 2 + i, SY + 1 + i, 1, 1, '1', indent='      '))
S.append('    </g>')
S.append(rect(SX, SY, SW, SH, 'T', cls='wsn-flash-a'))
S.append(rect(SX, SY, SW, SH, 'k', cls='wsn-flash-b'))
S.append('    <g class="wsn-scene-post">')
S.append(rect(SX, SY, SW, SH, 'B', indent='      '))
for i, wdt in enumerate([15, 19, 11, 21, 9, 17]):
    S.append(rect(SX + 1, SY + 1 + i * 2, 2, 1, 'G', cls='wsn-post-row',
                  style=f'--i: {i}', indent='      '))
    S.append(rect(SX + 3, SY + 1 + i * 2, wdt - 2, 1, 'g', cls='wsn-post-row',
                  style=f'--i: {i}', indent='      '))
S.append(rect(SX + 1, SY + 13, 4, 1, 'G', cls='wsn-post-row', style='--i: 6',
              indent='      '))
S.append('    </g>')
S.append('    <g class="wsn-scene-logo">')
S.append(rect(SX, SY, SW, SH, 'V', indent='      '))
ring = [
    '..ccb..',
    '.c...b.',
    'c.....b',
    'c..b..a',
    'c.....a',
    '.b...a.',
    '..baa..',
]
S.append(rects(98, 8, ring, indent='      '))
for i in range(4):
    S.append(rect(97 + i * 2, 17, 1, 1, 'b', cls='wsn-boot-dot',
                  style=f'--i: {i}', indent='      '))
S.append('    </g>')
S.append('    <g class="wsn-scene-desktop">')
S.append(rect(SX, SY, SW, SH, 'V', indent='      '))
S.append(rect(SX, SY + 14, SW, 1, 'D', indent='      '))       # taskbar
S.append(rect(SX + 1, SY + 14, 1, 1, 'b', indent='      '))    # launcher
S.append(rects(90, 8, [                                         # terminal
    '3333333333333',
    'BBBBBBBBBBBBB',
    'BGgggggBBBBBB',
    'BggggggggBBBB',
    'BgggBBBBBBBBB',
    'BBBBBBBBBBBBB',
], indent='      '))
S.append(rect(91, 13, 1, 1, 'G', cls='wsn-cursor', indent='      '))
S.append(rects(105, 10, [                                       # second window
    '333333333',
    'PPPPPPPPP',
    'PMMMMMMPP',
    'PMMMMPPPP',
    'PPPPPPPPP',
], indent='      '))
S.append('    </g>')
# static CRT scanlines over the screen: 2px lines on a 4px pitch, painted
# above every scene phase; low alpha so it whispers rather than stripes
S.append('    <g class="wsn-scan" style="opacity:0.12">')
for yy in range(SY * C, (SY + SH) * C, 4):
    S.append(f'      <rect x="{SX * C}" y="{yy}" width="{SW * C}" '
             f'height="2" fill="var(--px-outline)"/>')
S.append('    </g>')
S.append('  </g>')

# ============ glow spill — one geometry, one group per boot phase ============
# The monitor's light lands on the wall around the bezel, the desk in
# front, and pools on the floor below. Dithered outer edge (sparse pixels).
def spill(color, cls):
    out = [f'  <g class="{cls}">']
    # wall halo: thin solid band hugging the bezel, then dither falloff
    out.append(rect(88, 3, 28, 1, color))          # above the frame
    out.append(rect(85, 4, 1, 20, color))          # left side, 1 wide
    out.append(rect(118, 4, 1, 20, color))         # right side, 1 wide
    # dither falloff (checker-ish sparse pixels, denser near the band)
    for x, y in [(89, 2), (93, 2), (97, 2), (101, 2), (105, 2), (109, 2),
                 (113, 2), (91, 1), (99, 1), (107, 1),
                 (84, 5), (84, 9), (84, 13), (84, 17), (84, 21),
                 (83, 7), (83, 15), (83, 23),
                 (119, 5), (119, 9), (119, 13), (119, 17), (119, 21),
                 (120, 7), (120, 15), (120, 23)]:
        out.append(rect(x, y, 1, 1, color))
    # desk wash in front of the monitor + lit keyboard keys
    out.append(rect(84, 26, 36, 1, color))
    for x in (81, 83, 120):    # dithered desk edge (stops before the mug)
        out.append(rect(x, 26, 1, 1, color))
    for kx in (89, 92, 95, 98, 101):               # keyboard catches the light
        out.append(rect(kx, 25, 2, 1, color))
    # floor pool under the desk, narrowing downward, dithered rim
    out.append(rect(88, 57, 27, 1, color))
    out.append(rect(91, 58, 21, 1, color))
    out.append(rect(95, 59, 13, 1, color))
    for x, y in [(85, 57), (117, 57), (87, 58), (115, 58),
                 (89, 59), (93, 59), (109, 59), (113, 59),
                 (98, 60), (102, 60), (106, 60)]:
        out.append(rect(x, y, 1, 1, color))
    out.append('  </g>')
    return '\n'.join(out)

S.append(spill('D', 'wsn-sp-flash'))     # cold CRT-flash blue
S.append(spill('E', 'wsn-sp-post'))      # POST green
S.append(spill('w', 'wsn-sp-logo'))      # boot-logo amber
S.append(spill('V', 'wsn-sp-desktop'))   # desktop violet (persists settled)

sprites = '\n'.join(S)
tpl = open(os.path.join(HERE, 'wsn-template.html')).read()
open(os.path.join(OUT, 'workstation-night.html'), 'w').write(
    tpl.replace('@SPRITES@', sprites))
print(f'rects: {sprites.count("<rect")}')
