# Hero generators

The pixel-art heroes are not hand-edited HTML — each is generated from
an ASCII-pixel-map Python script in this directory plus a template that
carries the CSS choreography and the hero lifecycle script:

| hero | generator | template |
|---|---|---|
| `diagrams/linux-ai-setup/workstation-night.html` | `workstation-night.py` | `wsn-template.html` |
| `diagrams/linux-ai-setup/motherboard-city.html` | `motherboard-city.py` | `mbc-template.html` |

## Pipeline

1. Edit the generator (scene geometry, sprites, palette characters) or
   the template (keyframes, state CSS, aria-label). Never edit the
   generated diagram file directly — it is overwritten.
2. Run the generator: `python3 tools/heroes/workstation-night.py`
   (works from any cwd; paths are script-relative). It replaces the
   template's `@SPRITES@` marker with the generated rects and writes
   the diagram file.
3. `node scripts/build.js` — re-expands the managed sentinel blocks
   (the template ships them empty).
4. `npm run check` (`build --check` + validator), then preview in a
   browser / the gallery.

## Generator conventions

- 1 cell = 8 viewBox units; a 1200×500 hero is a 150×62 cell canvas.
- `COL` maps single characters to palette tokens (`var(--px-*)` ramps,
  dim fills). Sprites are ASCII rows (`.` = transparent); horizontal
  same-color runs merge into single `<rect>`s.
- Helpers: `rects(ox, oy, rows)` for ASCII maps, `rect(...)` for
  singles (supports `cls`/`style` for animation hooks like
  `class="wsn-pop" style="--i: 2"`), `dither(...)` for 2-cell checker
  transition rows.
- Animation classes referenced by the template's CSS are attached
  here; keep the two files in sync when adding a new animated group.
