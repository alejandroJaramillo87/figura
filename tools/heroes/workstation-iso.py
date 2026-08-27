#!/usr/bin/env python3
"""Generate workstation-iso: the workstation-night scene rebuilt as
isometric vector. Same subject and palette as the pixel-art original,
flat-shaded polygons on a 3D lattice instead of hand-placed sprites.

Composition note. An isometric floor always projects 1.73:1, so a
footprint wide enough to fill a 2.4:1 hero would be far too tall. The
scene is laid out along the ANTI-DIAGONAL instead: screen-horizontal is
u = x - z and screen-vertical is v = x + z, so spreading props over u
costs nothing vertically. The plant sits at low x / high z on the left,
the crates at high x / low z on the right, and both land at the same
screen height as the desk. Floor and walls bleed off every edge and are
cropped by the panel's overflow.

Framing was solved numerically: the focus cluster measures 1001 x 427
and lands at (99, 37)-(1101, 463) inside the 1200 x 500 viewBox.
"""
import isolib as I
from herolib import emit
from isolib import prism, iso, voxels

I.S = 17                  # viewBox units per lattice cell
OX, OY = 614.7, 55.3      # projection origin: lattice (0,0,0) on canvas
BASE_V = 20               # depth at which the intro wave starts counting

P = []


def add(*frags):
    P.extend(f for f in frags if f)


def box(x, y, z, w, h, d, ch, **kw):
    return prism(x, y, z, w, h, d, ch, ox=OX, oy=OY, **kw)


def obj(x, y, z, w, h, d, ch, i=None, **kw):
    """A prism that joins the depth-staggered intro wave. `--i` comes from
    the box's centre depth (x + z) so the scene assembles back to front,
    matching painter's order."""
    if i is None:
        i = max(0, int(round(x + z + (w + d) / 2)) - BASE_V)
    return box(x, y, z, w, h, d, ch, cls='wiso-band', style=f'--i: {i}', **kw)


# ============ room shell ============================================
# One prism each; the floor is a single polygon however far it extends.
add(obj(-46, -2, -46, 100, 2, 100, 'n', i=0, only='t'))
add(obj(0, 0, -1.2, 48, 18, 1.2, 'n', i=1, only='lt'))     # back-right wall
add(obj(-1.2, 0, 0, 1.2, 18, 48, 'n', i=1, only='rt'))     # back-left wall

# ============ window on the back-right wall =========================
# Lit surfaces take a flat `tone` — a light source reads flat, not faceted.
add(obj(15, 7, -0.05, 12, 7.6, 0.05, 'p', i=2, only='l', tone='px-dusk-1'))
add(obj(15.4, 7.6, -0.1, 11.2, 2.8, 0.05, 'p', i=2, only='l', tone='px-dusk-2'))
add(obj(15.4, 7.6, -0.15, 11.2, 0.55, 0.05, 'p', i=2, only='l', tone='px-dusk-3'))
add(obj(23.6, 12.0, -0.2, 1.2, 1.2, 0.05, 's', i=2, only='l', tone='px-sky-3'))
for bx, bw, bh in ((15.4, 1.5, 1.8), (16.9, 0.9, 2.6), (17.8, 1.4, 1.4),
                   (19.4, 1.1, 2.2), (20.5, 1.6, 1.6), (22.3, 1.0, 2.8),
                   (23.3, 1.3, 1.5), (24.6, 0.9, 2.3), (25.5, 1.6, 1.7)):
    add(obj(bx, 7.6, -0.18, bw, bh, 0.05, 'o', i=2, only='l',
            tone='px-outline'))
add(obj(21.0, 7, -0.25, 0.35, 7.6, 0.05, '0', i=2, only='l',
        tone='px-steel-2'))
add(obj(15, 10.6, -0.25, 12, 0.35, 0.05, '0', i=2, only='l',
        tone='px-steel-2'))
for fx, fy, fw, fh in ((14.6, 6.6, 12.8, 0.4), (14.6, 14.6, 12.8, 0.4),
                       (14.6, 6.6, 0.4, 8.4), (27.0, 6.6, 0.4, 8.4)):
    add(obj(fx, fy, -0.35, fw, fh, 0.35, '0', i=3, only='ltr'))

# ============ monitor spill on the floor ============================
# Emitted here, before the props that stand in it: painter's order is
# emission order, so the plant, desk legs and chair must come after.
# Two tiers give the pool a falloff edge instead of a hard rug border.
SPF = dict(only='t', cls='wiso-spill wiso-spill-1')
SPF2 = dict(only='t', cls='wiso-spill wiso-spill-2')
POOL = ((10.0, 22.0, 20.0, 9.5), (12.2, 17.0, 16.0, 9.0),
        (14.0, 13.8, 12.0, 8.0))
for n, (px, pz, pw, pd) in enumerate(POOL):
    add(box(px, 0.04 + n * 0.02, pz, pw, 0.02, pd, 'v',
            tone='violet-dim' if n == 0 else 'px-violet-1', **SPF))
    add(box(px, 0.05 + n * 0.02, pz, pw, 0.02, pd, 'g',
            tone='ok-dim' if n == 0 else 'px-green-1', **SPF2))

# ============ left flank: floor plant ===============================
add(obj(0.2, 0, 31.2, 3.0, 3.2, 3.0, '0', only='trl'))          # pot
add(obj(0.0, 3.2, 31.0, 3.4, 0.4, 3.4, '1', only='trl'))        # pot rim
add(iso(voxels([
    ['.GG.', 'GGGG', 'GGGG', '.GG.'],
    ['.G..', 'GGgG', '.GG.', '..G.'],
    ['....', '.Gg.', '....', '....'],
], ox=0, oy=4, oz=31), ox=OX, oy=OY, cls='wiso-band',
        wave_base=BASE_V, indent='  '))

# ============ right flank: stacked crates ===========================
add(obj(33.6, 0, 2.4, 4.2, 3.4, 4.2, '0', only='trl'))
add(obj(34.2, 3.4, 3.0, 3.0, 2.6, 3.0, 'd', only='trl'))
add(obj(38.4, 0, 4.0, 2.8, 2.0, 2.8, 'd', only='trl'))

# ============ centre: tower, desk, monitor, chair ===================
add(obj(26.6, 0, 9.0, 3.6, 8.4, 4.2, '1', only='trl'))          # tower
for vy in (2.2, 3.0, 3.8, 4.6):
    add(obj(30.2, vy, 9.4, 0.05, 0.4, 3.4, 'o', only='r', tone='px-outline'))
add(box(30.2, 7.0, 9.8, 0.06, 0.5, 0.5, 'g', only='r',
        tone='px-green-2', cls='wiso-led'))

for lx, lz in ((12.4, 11.2), (24.4, 11.2), (12.4, 18.0), (24.4, 18.0)):
    add(obj(lx, 0, lz, 0.7, 6.0, 0.7, '0', only='trl'))         # desk legs
add(obj(12, 6.0, 10.8, 13.5, 0.6, 8.2, '1', only='trl'))        # desk top

# desk-surface wash, over the desk top and under everything on it
SPD = dict(only='t', cls='wiso-spill wiso-spill-1')
add(box(13.6, 6.63, 13.2, 10.4, 0.02, 5.2, 'v', tone='px-violet-1', **SPD))
SPD2 = dict(only='t', cls='wiso-spill wiso-spill-2')
add(box(13.6, 6.64, 13.2, 10.4, 0.02, 5.2, 'g', tone='px-green-1', **SPD2))

add(obj(17.6, 6.6, 12.2, 3.6, 0.35, 2.2, '0', only='trl'))      # monitor base
add(obj(18.8, 6.9, 12.8, 1.2, 1.6, 0.8, '0', only='trl'))       # neck
add(obj(15.0, 8.3, 11.9, 9.2, 6.2, 0.9, '1', only='trl'))       # panel

# screen: two flat states the ambient loop cross-cuts (desktop / terminal)
SC = dict(only='l', cls='wiso-scr wiso-scr-1')
add(box(15.4, 8.7, 12.85, 8.4, 5.4, 0.05, 'v', tone='px-violet-1', **SC))
add(box(15.9, 12.3, 12.9, 3.4, 1.2, 0.05, 'v', tone='px-violet-2', **SC))
add(box(15.9, 9.4, 12.9, 5.6, 2.3, 0.05, 'v', tone='px-violet-3', **SC))
SC2 = dict(only='l', cls='wiso-scr wiso-scr-2')
add(box(15.4, 8.7, 12.95, 8.4, 5.4, 0.05, 'g', tone='px-green-1', **SC2))
add(box(15.9, 9.4, 13.0, 6.4, 3.7, 0.05, 'g', tone='px-green-2', **SC2))
add(box(15.9, 13.1, 13.0, 2.2, 0.5, 0.05, 'g', tone='px-green-3', **SC2))

add(obj(15.4, 6.6, 14.6, 6.4, 0.35, 2.2, '0', only='trl'))      # keyboard
add(obj(23.2, 6.6, 15.2, 0.9, 0.35, 1.3, '0', only='trl'))      # mouse
add(obj(12.8, 6.6, 15.0, 1.3, 1.5, 1.3, 'a', only='trl'))       # mug
add(obj(14.1, 7.1, 15.3, 0.4, 0.7, 0.7, 'a', only='trl'))       # handle

# chair: pulled clear of the desk toward the viewer, chunky enough to
# hold a silhouette against the floor pool it stands in
add(obj(14.4, 0, 26.4, 5.2, 0.5, 0.9, 'd', only='trl'))         # base cross
add(obj(16.4, 0, 24.6, 1.2, 0.5, 4.4, 'd', only='trl'))
add(obj(16.4, 0.5, 26.4, 1.2, 3.3, 1.2, '0', only='trl'))       # post
add(obj(14.6, 3.8, 24.8, 5.0, 0.7, 4.2, '1', only='trl'))       # seat
add(obj(14.6, 4.5, 28.6, 5.0, 4.5, 0.8, '1', only='trl'))       # back

emit('wiso-template.html', 'showcase/workstation-iso.html', '\n'.join(P))
