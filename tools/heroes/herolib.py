"""herolib — shared machinery for hero pixel-art generators.

Every hero generator imports from this module; per-generator helper
copies and per-hero COL additions are forbidden (see README.md). The
palette character alphabet below is canonical: new characters are added
here (mapped to existing ramp tokens) or not at all — ramp tokens
themselves are a closed set in shared/tokens.css.

Conventions: 1 cell = C viewBox units; a 1200x500 hero is a 150x62 cell
canvas. '.' in an ASCII row is transparent; horizontal same-color runs
merge into a single <rect>.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DIAGRAMS = os.path.join(HERE, '..', '..', 'diagrams')

C = 8  # viewBox units per cell

# Canonical palette character alphabet (char -> palette token).
COL = {
    # base / dim tokens
    'B': 'var(--bg)', 'P': 'var(--panel)', 'H': 'var(--panel-hover)',
    'M': 'var(--muted)', 'T': 'var(--text)',
    'V': 'var(--violet-dim)', 'v': 'var(--violet)', 'D': 'var(--accent-dim)',
    'E': 'var(--ok-dim)', 'w': 'var(--warn-dim)', 'R': 'var(--hot)',
    'L': 'var(--line)',
    # sprite ramps (shadow -> mid -> highlight)
    'o': 'var(--px-outline)',
    '1': 'var(--px-steel-1)', '2': 'var(--px-steel-2)',
    '3': 'var(--px-steel-3)', '4': 'var(--px-steel-4)',
    'a': 'var(--px-amber-1)', 'b': 'var(--px-amber-2)', 'c': 'var(--px-amber-3)',
    'g': 'var(--px-green-1)', 'G': 'var(--px-green-2)', 'e': 'var(--px-green-3)',
    's': 'var(--px-sky-1)', 'S': 'var(--px-sky-2)', 'k': 'var(--px-sky-3)',
    'p': 'var(--px-dusk-1)', 'r': 'var(--px-dusk-2)', 'h': 'var(--px-dusk-3)',
    'y': 'var(--px-violet-1)', 'Y': 'var(--px-violet-2)', 'z': 'var(--px-violet-3)',
    'x': 'var(--px-hot-1)', 'X': 'var(--px-hot-2)', 'Z': 'var(--px-hot-3)',
}


def rects(ox, oy, rows, indent='    '):
    """Emit an ASCII pixel map at cell offset (ox, oy)."""
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
    """Emit a single cell-aligned rect; cls/style attach animation hooks
    (e.g. cls='wsn-pop', style='--i: 2')."""
    a = f' class="{cls}"' if cls else ''
    s = f' style="{style}"' if style else ''
    return (f'{indent}<rect{a}{s} x="{cx*C}" y="{cy*C}" width="{cw*C}" '
            f'height="{ch_*C}" fill="{COL[color]}"/>')


def dither(ox, y, w, ch, phase=0):
    """2-cell checker blocks every 4 cells — band-transition dither."""
    return '\n'.join(rect(x, y, 2, 1, ch)
                     for x in range(ox + phase * 2, ox + w - 1, 4))


def dither_row(y, ch, phase=0, width=150):
    """Full-width band-transition dither (chunky band edge)."""
    return dither(0, y, width, ch, phase)


def emit(template, out_relpath, sprites):
    """Substitute @SPRITES@ in tools/heroes/<template> and write
    diagrams/<out_relpath>. Managed blocks in the template ship empty;
    run `node scripts/build.js` afterwards to expand them."""
    tpl = open(os.path.join(HERE, template)).read()
    if '@SPRITES@' not in tpl:
        raise SystemExit(f'[ERROR] {template}: no @SPRITES@ marker')
    out_path = os.path.join(DIAGRAMS, out_relpath)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, 'w').write(tpl.replace('@SPRITES@', sprites))
    print(f'rects: {sprites.count("<rect")}')
