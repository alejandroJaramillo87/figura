#!/usr/bin/env python3
"""Generate three-vessels sprites: 1 cell = 8 viewBox units, 150x62
canvas. Three container vessels of different silhouettes stand on one
shared foundation slab (the sandboxing series' shared hardening floor):
a squat sealed appliance (sky ramp, status LED), a tall open-top hopper
with a sight-glass fill gauge (amber ramp), and a box with one narrow
gated egress pipe (violet ramp). The slab lands first in the intro."""
from herolib import dither, emit, rect, rects

S = []

# ============ backdrop: sparse dust pixels for depth ============
for x, y in [(28, 10), (52, 15), (76, 7), (104, 12), (132, 9), (12, 18)]:
    S.append(rect(x, y, 1, 1, 'P'))

# ============ foundation slab (pop 0) — the shared floor ============
S.append('  <g class="tvs-pop" style="--i: 0">')
S.append(rect(0, 50, 150, 1, 'e'))    # lit top surface
S.append(rect(0, 51, 150, 1, 'G'))
S.append(rect(0, 52, 150, 2, 'g'))
S.append(dither(0, 54, 150, 'g'))     # transition into the dark base
S.append(rect(0, 55, 150, 7, 'o'))    # dark ground mass to frame bottom
S.append('  </g>')

# ============ vessel 1 (pop 1): sealed inference appliance ============
# Squat wide box, sky ramp, no openings; horizontal seams read as a
# machined enclosure. Shadow column on the right (light from the left).
S.append('  <g class="tvs-pop" style="--i: 1">')
S.append(rect(15, 50, 32, 1, 'o'))    # contact shadow on the slab
cap1 = '.' + 'o' * 28 + '.'
lit1 = 'o' + 'k' * 27 + 's' + 'o'
mid1 = 'o' + 'S' * 27 + 's' + 'o'
seam1 = 'o' + 's' * 28 + 'o'
S.append(rects(16, 32, [
    cap1, lit1,
    mid1, mid1, mid1,
    seam1,
    mid1, mid1, mid1,
    seam1,
    mid1, mid1, mid1,
    seam1,
    mid1, mid1,
    seam1,
    cap1,
]))
S.append(rect(20, 35, 1, 1, 'e', cls='tvs-led'))   # status LED
S.append('  </g>')

# ============ vessel 2 (pop 2): open-top training hopper ============
# Tallest sprite, amber ramp, open top showing a dark interior, and a
# sight-glass gauge on the front wall where the charge level animates.
S.append('  <g class="tvs-pop" style="--i: 2">')
S.append(rect(61, 50, 26, 1, 'o'))    # contact shadow
rim = '.' + 'o' * 22 + '.'
mouth = 'o' + 'B' * 22 + 'o'
lip = 'o' + 'c' * 21 + 'a' + 'o'
wall = 'o' + 'b' * 21 + 'a' + 'o'
base = 'o' + 'a' * 22 + 'o'
S.append(rects(62, 18, [rim, mouth, mouth, lip] + [wall] * 26 + [base, rim]))
S.append(rect(71, 24, 4, 22, 'o'))    # sight-glass frame
S.append(rect(72, 25, 2, 20, 'B'))    # sight-glass channel
# charge-level flipbook frames: low -> mid -> full -> (empty = dump)
S.append('    <g class="tvs-chg tvs-chg-1">')
S.append(rect(72, 40, 2, 5, 'c', indent='      '))
S.append('    </g>')
S.append('    <g class="tvs-chg tvs-chg-2">')
S.append(rect(72, 33, 2, 12, 'c', indent='      '))
S.append('    </g>')
S.append('    <g class="tvs-chg tvs-chg-3">')
S.append(rect(72, 25, 2, 20, 'c', indent='      '))
S.append('    </g>')
S.append('  </g>')

# ============ vessel 3 (pop 3): agent box with gated egress pipe ============
# Medium box, violet ramp, one narrow pipe exiting frame-right through a
# bright gate collar — the only opening any vessel has.
S.append('  <g class="tvs-pop" style="--i: 3">')
S.append(rect(99, 50, 24, 1, 'o'))    # contact shadow
cap3 = '.' + 'o' * 20 + '.'
top3 = 'o' + 'z' * 19 + 'y' + 'o'
mid3 = 'o' + 'Y' * 19 + 'y' + 'o'
base3 = 'o' + 'y' * 20 + 'o'
S.append(rects(100, 30, [cap3, top3] + [mid3] * 16 + [base3, cap3]))
# pipe: outlined violet tube with a dark channel, cut through the box wall
S.append(rect(122, 37, 21, 1, 'o'))   # outer wall top
S.append(rect(122, 38, 21, 1, 'Y'))   # tube top
S.append(rect(122, 39, 21, 2, 'B'))   # channel
S.append(rect(122, 41, 21, 1, 'Y'))   # tube bottom
S.append(rect(122, 42, 21, 1, 'o'))   # outer wall bottom
S.append(rect(120, 39, 2, 2, 'B'))    # opening through the box wall
# gate collar straddling the pipe
S.append(rect(126, 34, 2, 1, 'o'))
S.append(rect(126, 35, 2, 4, 'z'))
S.append(rect(126, 41, 2, 4, 'z'))
S.append(rect(126, 45, 2, 1, 'o'))
# egress-pulse flipbook frames: one bright packet metered along the pipe
S.append('    <g class="tvs-px tvs-px-1">')
S.append(rect(123, 39, 2, 2, 'z', indent='      '))
S.append('    </g>')
S.append('    <g class="tvs-px tvs-px-2">')
S.append(rect(130, 39, 2, 2, 'z', indent='      '))
S.append('    </g>')
S.append('    <g class="tvs-px tvs-px-3">')
S.append(rect(137, 39, 2, 2, 'z', indent='      '))
S.append('    </g>')
S.append('  </g>')

emit('tvs-template.html', 'sandboxing/three-vessels.html', '\n'.join(S))
