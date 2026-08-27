"""Truchet loops — the generative treatment's emergence piece.

A grid of Smith-Truchet tiles. Each tile flips a coin and lays two
quarter-circle arcs between the midpoints of its edges; because both
orientations land on the same four midpoints, neighbouring tiles always
connect. Nothing joins them up on purpose, and yet the arcs chain into
closed loops with a heavy-tailed size distribution -- a mass of tiny
two-arc rings, a thin middle, and one giant loop wandering most of the
frame. That is the whole subject: the rule is a coin flip, the structure
is not in the rule.

Composition is chosen, not searched. Unlike the attractor -- whose form
had to be rotated into a frame it never really fits -- a 24x10 grid of
50-unit tiles divides the 1200x500 hero exactly. The seed picks which
picture, not whether there is one: every seed tried produced a giant
component carrying 10-28% of the ink. This one runs x 225-1025 and
y 75-475, which is what makes the piece read at thumbnail size instead
of as wallpaper.

Four interior cells are left out of the tiling and emitted twice, once
per orientation, for the ambient loop. The loops that would pass through
them end there as loose ends -- honest, because those cells genuinely
have not settled.
"""
import genlib as G
from herolib import emit

COLS, ROWS, TILE = 24, 10, 50
SEED = 1
FLIP = ((5, 6), (10, 2), (15, 7), (19, 3))  # interior, spread, non-adjacent

# Strata by arc count, cut on the measured distribution and not by
# equal-count terciles -- the tail is heavy, so terciles put a third of
# the ink in the top band and the piece came out reading as mostly
# highlight. The sizes here run ... 24, 27, 38, 96: a real gap, and the
# cut goes in it, which leaves the giant loop alone in the top band at
# 20% of the ink against a 56% body and a 23% haze. Three strata against
# one --px-* ramp's three bands, so no new tokens (the isolib trick).
STRATA = ((4, 'trl-small'), (48, 'trl-mid'), (10 ** 9, 'trl-large'))

_, arcs = G.truchet_arcs(COLS, ROWS, G.rng(SEED), TILE, skip=FLIP)
comps = sorted(G.chain(arcs), key=len)

body = []

# Undecided cells first, so they paint behind the field and arrive before
# it. One --i per cell; both orientations share it so they stay in phase.
for i, (c, r) in enumerate(FLIP):
    for o, cls in ((0, 'trl-flip-a'), (1, 'trl-flip-b')):
        d = ' '.join(G.arc_d([a], TILE, TILE // 2)
                     for a in G.tile_arcs(c, r, o, TILE))
        body.append(f'  <path class="{cls}" style="--i: {i}" d="{d}"/>')

# Then the components, smallest first: that is both the paint order (the
# giant ends up on top, where it belongs) and the reveal order, so the
# intro assembles the field from the small scale up and the one loop that
# crosses the frame lands last.
for i, comp in enumerate(comps, start=len(FLIP)):
    cls = next(c for lim, c in STRATA if len(comp) <= lim)
    body.append(f'  <path class="trl-run {cls}" style="--i: {i}" '
                f'd="{G.arc_d(comp, TILE, TILE // 2)}"/>')

emit('trl-template.html', 'showcase/truchet-loops.html', '\n'.join(body))
