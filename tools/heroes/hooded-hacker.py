#!/usr/bin/env python3
"""Generate hooded-hacker sprites: 1 cell = 8 viewBox units, 150x62
canvas. One large frontal hooded figure behind an open laptop, in the
chunky security-icon style: fat outline, dark violet hood, face cavity
with glowing eyes, screen light rimming the chest, and green code rain
falling in the background columns either side of the sprite."""
import random

from herolib import emit, rect, rects

S = []

# Sprite map authored in the mockup alphabet, translated to COL chars:
# hood outer -> violet-dim, hood front -> px-violet-1, laptop -> panel
# shades. Eyes, chest glow, lit screen edge, and logo are overlays so
# the template can reveal and animate them independently.
TR = {'.': '.', 'o': 'o', 'B': 'B', 'h': 'V', 'H': 'y', 'L': 'H', 'l': 'P'}
MAP = [
    '............oooooooooo............',
    '..........oohhhhhhhhhhoo..........',
    '.........ohhhhhhhhhhhhhho.........',
    '........ohhhhhhhhhhhhhhhho........',
    '.......ohhhhhhhhhhhhhhhhho........',
    '.......ohhhhHHHHHHHHhhhhho........',
    '......ohhhHHHHHHHHHHHHhhho........',
    '......ohhhHHooooooooHHhhho........',
    '......ohhHooBBBBBBBBooHhho........',
    '.....ohhHoBBBBBBBBBBBBoHho........',
    '.....ohhHoBBBBBBBBBBBBoHho........',
    '.....ohhHoBBBBBBBBBBBBoHho........',
    '.....ohhHoBBBBBBBBBBBBoHho........',
    '.....ohhHoBBBBBBBBBBBBoHho........',
    '.....ohhHoBBBBBBBBBBBBoHho........',
    '.....ohhHooBBBBBBBBBBooHho........',
    '....ohhHHHooooooooooooHHho........',
    '....ohhHHHHHHHHHHHHHHHHHHho.......',
    '...ohhHHHHHHHHHHHHHHHHHHHHho......',
    '...ohhHHHHHHHHHHHHHHHHHHHHho......',
    '..ohhHHHHHHHHHHHHHHHHHHHHHHo......',
    '..ohHHHHHHHHHHHHHHHHHHHHHHHo......',
    '.ohhHHHHHHHHHHHHHHHHHHHHHHHHo.....',
    '.ohHHHHHHHHHHHHHHHHHHHHHHHHHo.....',
    'ohhHHHHHHHHHHHHHHHHHHHHHHHHHHo....',
    '.oooooooooooooooooooooooooooo.....',
    '.oLLLLLLLLLLLLLLLLLLLLLLLLLLo.....',
    '.oLLLLLLLLLLLLLLLLLLLLLLLLLLo.....',
    '.oLLLLLLLLLLLLLLLLLLLLLLLLLLo.....',
    '.oLLLLLLLLLLLLLLLLLLLLLLLLLLo.....',
    '.oLLLLLLLLLLLLLLLLLLLLLLLLLLo.....',
    '.oLLLLLLLLLLLLLLLLLLLLLLLLLLo.....',
    'ooooooooooooooooooooooooooooooo...',
    'olLLLLLLLLLLLLLLLLLLLLLLLLLLLlo...',
    'ooooooooooooooooooooooooooooooo...',
]
OX, OY = 58, 18   # sprite origin: 34x35 map centered in the 150x62 frame


def stream(x, y0, tall, indent='      '):
    """One code-rain stream: dim trail pixels above a bright 2-cell head."""
    out = [rect(x, y0 + k, 1, 1, 'g', indent=indent) for k in range(0, tall - 2, 2)]
    out.append(rect(x, y0 + tall - 2, 1, 2, 'G', indent=indent))
    return '\n'.join(out)


# ============ code rain: 3 flipbook frames, columns either side ============
# Same columns in every frame, stream shifted downward per frame so the
# cycle reads as falling. Alternate columns sit in a half-alpha group.
random.seed(11)
cols = [(x, random.randint(2, 26), random.randint(6, 10))
        for x in list(range(6, 52, 8)) + list(range(100, 146, 8))]
for f in range(1, 4):
    S.append(f'  <g class="hhk-rain hhk-rain-{f}">')
    for i, (x, y0, tall) in enumerate(cols):
        y = y0 + (f - 1) * (tall + 2) // 3
        if i % 2:
            S.append('    <g style="opacity:0.5">')
            S.append(stream(x + 3, y + 4, tall))
            S.append('    </g>')
        else:
            S.append(stream(x, y, tall, indent='    '))
    S.append('  </g>')

# ============ hacker (pop 0): hood, torso, laptop ============
S.append('  <g class="hhk-pop" style="--i: 0">')
S.append(rect(OX, 54, 31, 1, 'o'))    # ground shadow under the laptop
S.append(rects(OX, OY, [''.join(TR[c] for c in row) for row in MAP]))

# eyes (rows 11-12 of the map)
S.append(rect(OX + 12, OY + 11, 2, 2, 'G', cls='hhk-eye', style='--i: 0'))
S.append(rect(OX + 18, OY + 11, 2, 2, 'G', cls='hhk-eye', style='--i: 1'))

# screen elements: lit lid edge + logo, revealed together at "screen wake"
S.append('    <g class="hhk-scr">')
S.append(rect(OX + 2, OY + 26, 26, 1, 'e', indent='      '))
S.append(rect(OX + 14, OY + 28, 1, 2, 'o', indent='      '))
S.append(rect(OX + 15, OY + 28, 2, 2, 'G', indent='      '))
S.append(rect(OX + 17, OY + 28, 1, 2, 'o', indent='      '))
S.append('    </g>')

# chest screen-glow, two flipbook patterns (screen content changing)
S.append('    <g class="hhk-glow hhk-glow-1">')
for x, y, w, c in [(13, 17, 6, 'Y'),
                   (12, 18, 2, 'Y'), (14, 18, 4, 'z'), (18, 18, 2, 'Y'),
                   (11, 19, 2, 'Y'), (13, 19, 6, 'z'), (19, 19, 2, 'Y'),
                   (11, 20, 2, 'Y'), (13, 20, 6, 'z'), (19, 20, 2, 'Y'),
                   (12, 21, 8, 'Y')]:
    S.append(rect(OX + x, OY + y, w, 1, c, indent='      '))
S.append('    </g>')
S.append('    <g class="hhk-glow hhk-glow-2">')
for x, y, w, c in [(14, 17, 5, 'Y'),
                   (13, 18, 2, 'Y'), (15, 18, 4, 'z'), (19, 18, 1, 'Y'),
                   (12, 19, 2, 'Y'), (14, 19, 5, 'z'), (19, 19, 2, 'Y'),
                   (12, 20, 3, 'Y'), (15, 20, 4, 'z'), (19, 20, 1, 'Y'),
                   (13, 21, 7, 'Y')]:
    S.append(rect(OX + x, OY + y, w, 1, c, indent='      '))
S.append('    </g>')
S.append('  </g>')

# sparse static dust pixels for depth
for x, y in [(20, 8), (44, 14), (98, 6), (126, 16), (12, 40), (140, 36)]:
    S.append(rect(x, y, 1, 1, 'P'))

emit('hhk-template.html', 'sandboxing/hooded-hacker.html', '\n'.join(S))
