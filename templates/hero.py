#!/usr/bin/env python3
"""Generate {{NAME}} sprites: 1 cell = 8 viewBox units, 150x62 canvas.
TODO: one-line scene description."""
from herolib import emit, rect, rects

S = []

# TODO: author the scene as ASCII pixel maps (see README.md).
# Group sprites by intro stage; attach animation classes/stagger via
# rect(..., cls='{{ABBR}}-pop', style='--i: 0').
S.append('  <g class="{{ABBR}}-pop" style="--i: 0">')
S.append(rects(70, 28, [
    '.111.',
    '12321',
    '.111.',
]))
S.append('  </g>')

emit('{{ABBR}}-template.html', '{{SLUG}}/{{NAME}}.html', '\n'.join(S))
