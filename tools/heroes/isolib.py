"""isolib — shared machinery for isometric-vector hero generators.

The pixel-art heroes (see herolib.py) place flat `<rect>` sprites on a 2D
cell grid. Isometric heroes place *volumes* on a 3D lattice and project
them to flat-shaded `<polygon>` faces. Same palette, same hero lifecycle,
same generator + template pair convention — only the drawing primitive
changes.

Three properties make the isometric case cheap, and all three are load
bearing:

1. Only three faces of an axis-aligned box are ever visible from the
   +x+y+z octant: +y (top), +x (down-right), +z (down-left). Everything
   else is culled before it is ever emitted.
2. A box shows exactly three tones, and every --px-* ramp has exactly
   three bands. Top = highlight, right = mid, left = shadow, always.
   That is why the shading reads as correct with no lighting math and
   no new palette tokens.
3. Painter's order for equal-size cubes on a lattice is exactly
   `x + y + z` ascending. No depth sort, no BSP, no z-fighting.

Two primitives, and picking the right one is the whole size story:

- `prism()` for anything regular — a desk top, a wall, a tower, a floor.
  One box is 3 polygons regardless of how many cells it spans. A desk
  top voxelized would be 220 polygons; as a prism it is 3.
- `voxels()` + `iso()` for irregular detail clusters, where the shape
  genuinely varies cell by cell. Faces are culled against neighbours and
  grouped into `<g>` bands by depth.

Conventions: 1 lattice cell = `S` viewBox units (a generator may raise
`isolib.S` to scale a scene); y is up; '.' in an ASCII row is empty.
"""
import math
import os
from itertools import groupby

HERE = os.path.dirname(os.path.abspath(__file__))
DIAGRAMS = os.path.join(HERE, '..', '..', 'diagrams')

S = 8            # viewBox units per lattice cell edge (generators may raise)
COS30 = math.sqrt(3) / 2
SIN30 = 0.5
INFLATE = 1.015  # face overscale: closes antialiasing seams between
                 # adjacent same-color faces without any stroke attribute

# Ramp character -> (top, right, left) palette tokens. Shadows cool,
# highlights warm, mirroring herolib.COL's ramp logic. This alphabet is
# canonical: new characters map to existing ramps or are not added, and
# the --px-* set in shared/tokens.css stays closed.
RAMP = {
    '1': ('px-steel-4', 'px-steel-3', 'px-steel-2'),   # body, lit
    '0': ('px-steel-3', 'px-steel-2', 'px-steel-1'),   # body, in shadow
    'd': ('px-steel-2', 'px-steel-1', 'px-outline'),   # unlit surface
    'n': ('px-steel-1', 'px-outline', 'px-outline'),   # night: floor, walls
    'a': ('px-amber-3', 'px-amber-2', 'px-amber-1'),
    'g': ('px-green-3', 'px-green-2', 'px-green-1'),
    'G': ('px-green-2', 'px-green-1', 'px-outline'),   # foliage in shadow
    's': ('px-sky-3', 'px-sky-2', 'px-sky-1'),
    'p': ('px-dusk-3', 'px-dusk-2', 'px-dusk-1'),
    'v': ('px-violet-3', 'px-violet-2', 'px-violet-1'),
    'x': ('px-hot-3', 'px-hot-2', 'px-hot-1'),
    'o': ('px-outline', 'px-outline', 'px-outline'),   # silhouette / void
}

FACE_IDX = {'t': 0, 'r': 1, 'l': 2}


def _corners(w, h, d):
    """Corner rings for the three visible faces of a w x h x d box, as
    (dx, dy, dz) offsets from its origin corner."""
    return {
        't': ((0, h, 0), (w, h, 0), (w, h, d), (0, h, d)),   # +y  top
        'r': ((w, h, 0), (w, h, d), (w, 0, d), (w, 0, 0)),   # +x  down-right
        'l': ((0, h, d), (w, h, d), (w, 0, d), (0, 0, d)),   # +z  down-left
    }


def project(x, y, z, ox=0.0, oy=0.0):
    """Lattice point (x, y, z) -> 2D viewBox point. y is up."""
    return ((x - z) * COS30 * S + ox,
            (x + z) * SIN30 * S - y * S + oy)


def _inflate(pts):
    """Overscale a face about its centroid to close antialiasing seams."""
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return [(cx + (px - cx) * INFLATE, cy + (py - cy) * INFLATE)
            for px, py in pts]


def _poly(x, y, z, ring, token, ox, oy, indent):
    """One flat-shaded face. Coordinates round to 1dp — float noise is
    the single biggest cause of bloated SVG output."""
    pts = _inflate([project(x + dx, y + dy, z + dz, ox, oy)
                    for dx, dy, dz in ring])
    d = ' '.join(f'{round(px, 1):g},{round(py, 1):g}' for px, py in pts)
    return f'{indent}<polygon fill="var(--{token})" points="{d}"/>'


def prism(x, y, z, w, h, d, ch, only='trl', tone=None,
          cls='', style='', ox=0.0, oy=0.0, indent='    '):
    """The three visible faces of an axis-aligned box — 3 polygons for any
    size. This is the primary primitive; reach for voxels only when the
    shape genuinely varies cell by cell.

    `only` selects faces ('t' top, 'r' right, 'l' left) — use it for
    inset surfaces like a screen, or to drop a face that is buried.
    `tone` forces one palette token on every face (emissive surfaces read
    flat, not shaded). `cls`/`style` wrap the faces in an animation group.
    """
    rings = _corners(w, h, d)
    out = []
    for f in only:
        token = tone if tone else RAMP[ch][FACE_IDX[f]]
        out.append(_poly(x, y, z, rings[f], token, ox, oy,
                         indent + ('  ' if cls or style else '')))
    if cls or style:
        a = f' class="{cls}"' if cls else ''
        s = f' style="{style}"' if style else ''
        return f'{indent}<g{a}{s}>\n' + '\n'.join(out) + f'\n{indent}</g>'
    return '\n'.join(out)


def voxels(layers, ox=0, oy=0, oz=0, vox=None):
    """Stack of 2D ASCII slabs -> voxel dict.

    `layers[i]` is the slab at y = oy + i: a list of rows where the row
    index is z (depth, toward the viewer's lower left) and the character
    index is x. '.' is empty. herolib.rects()'s model with one more axis.
    """
    if vox is None:
        vox = {}
    for iy, rows in enumerate(layers):
        for iz, row in enumerate(rows):
            for ix, ch in enumerate(row):
                if ch != '.':
                    vox[(ox + ix, oy + iy, oz + iz)] = ch
    return vox


def fill(vox, x, y, z, w, h, d, ch):
    """Fill an axis-aligned solid into a voxel dict (detail clusters that
    need per-cell culling against their neighbours; use prism() for
    anything you would otherwise draw as one box)."""
    for bx in range(x, x + w):
        for by in range(y, y + h):
            for bz in range(z, z + d):
                vox[(bx, by, bz)] = ch
    return vox


def cull(vox):
    """Visible faces as (x, y, z, char, face), sorted back-to-front.

    A face is hidden exactly when the neighbour cell on that side is
    filled. Sorting by x+y+z is the painter's order (see module docstring).
    """
    out = []
    for key in sorted(vox, key=lambda k: k[0] + k[1] + k[2]):
        x, y, z = key
        ch = vox[key]
        if (x, y + 1, z) not in vox:
            out.append((x, y, z, ch, 't'))
        if (x + 1, y, z) not in vox:
            out.append((x, y, z, ch, 'r'))
        if (x, y, z + 1) not in vox:
            out.append((x, y, z, ch, 'l'))
    return out


def iso(vox, ox=0.0, oy=0.0, cls='', bands=True, wave_base=None, indent='  '):
    """Project a voxel set to SVG, culled and in painter's order.

    With `bands` (the default) faces are grouped into one `<g>` per depth
    layer carrying `class=cls` and `style="--i: <depth>"`, so a template
    animates a few dozen groups instead of every polygon and the class set
    stays fixed (the validator's hero-sync check compares classes
    symmetrically). Pass bands=False for a prop that animates as one unit.

    Groups are ordered by painter depth (x+y+z), but `--i` is measured on
    x+z when `wave_base` is given, so a voxel cluster staggers on the same
    clock as the prisms around it rather than on its own local minimum.
    """
    faces = cull(vox)
    if not faces:
        return ''
    rings = _corners(1, 1, 1)
    def one(f, ind):
        x, y, z, ch, fc = f
        return _poly(x, y, z, rings[fc], RAMP[ch][FACE_IDX[fc]], ox, oy, ind)
    if not bands:
        return '\n'.join(one(f, indent) for f in faces)
    out = []
    base = min(f[0] + f[1] + f[2] for f in faces)
    for depth, group in groupby(faces, key=lambda f: f[0] + f[1] + f[2]):
        group = list(group)
        if wave_base is None:
            i = depth - base
        else:
            i = max(0, min(f[0] + f[2] for f in group) - wave_base)
        attr = f' class="{cls}"' if cls else ''
        out.append(f'{indent}<g{attr} style="--i: {i}">')
        for f in group:
            out.append(one(f, indent + '  '))
        out.append(f'{indent}</g>')
    return '\n'.join(out)


def extent(corners, ox=0.0, oy=0.0):
    """Projected bounding box of lattice points, as (x0, y0, x1, y1) —
    for framing a scene against the 1200x500 viewBox while authoring."""
    pts = [project(*c, ox, oy) for c in corners]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (round(min(xs), 1), round(min(ys), 1),
            round(max(xs), 1), round(max(ys), 1))
