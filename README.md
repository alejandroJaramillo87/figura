# figura

A growing library of animated, interactive technical diagrams — SVG + CSS +
vanilla JS, one self-contained HTML file per diagram — for the
[Curiosity Chronicles](https://alejandrojaramillo87.github.io/curiosity-chronicles/)
blog (LLM internals, mech interp, inference engines), and static diagrams
exported as SVG images for the ai-experiments docs site.

## How it works

- Each diagram is a standalone HTML page you can open directly in a browser.
  The portion between `<!-- fg:embed-start -->` / `<!-- fg:embed-end -->` is a
  fully self-contained fragment (scoped styles, namespaced SVG ids, IIFE JS).
- The blog mounts this repo as a git submodule at `static/diagrams` and a Hugo
  shortcode inlines the fragment at build time — no iframes, no runtime deps:

  ```text
  {{</* diagram name="inference-loop/kv-cache-fill" caption="The KV cache during decode." */>}}
  ```

- Diagrams are authored by a coding agent from diagram notes, following the
  contract in [CLAUDE.md](CLAUDE.md) and using existing diagrams as style
  reference — the library grows organically with each post.

## Documentation

Detailed project docs live in [docs/](docs/README.md): architecture
(the managed-blocks system and scripts pipeline), blog integration
(submodule + shortcode + release flow), development workflow, and the
diagram authoring guide. [CLAUDE.md](CLAUDE.md) remains the enforced
generation contract.

## Layout

```text
CLAUDE.md        generation contract (conventions, palette, patterns)
index.html       gallery — every diagram inlined, first one twice (collision check)
manifest.json    diagram index {id, path, title, kind, consumers, description}
shared/
  tokens.css     palette source of truth: classic dark, shared with the
                 blog's tokens (build.js derives the per-diagram palette blocks)
  runtime/       canonical managed-block sources (panel, timeline,
                 captions, toggles, per-copy ids, reduced motion) stamped
                 into every fragment by scripts/build.js
  effects.css    effects catalog: glow, sweep, comet, draw-in, ripple,
                 shimmer, flash (copy-source patterns)
  snippets.js    copy-source helpers for step-triggered effects (never loaded)
  preview.css    page chrome for standalone/gallery viewing only
scripts/
  new-diagram.js scaffold a diagram from templates/ with blocks pre-expanded
  build.js       re-expand managed blocks (--check fails on drift)
  validate.js    contract linter: block sets per kind, scoping, tokens,
                 ids, reduced motion, a11y, self-containment, manifest sync
  export-svg.js  write static diagrams to dist/ as standalone SVG images
  lib/fragment.js shared parsing helpers (embed split, block pairing,
                 block versions and kinds, palette generation)
  lib/cli.js     strict argument parsing shared by all four scripts
docs/            project documentation (architecture, blog integration,
                 development, authoring)
templates/       step-timeline, hover-inspect, toggle, ambient, static scaffolds
diagrams/<consumer-dir>/<kebab-name>.html
```

Tooling is zero-dependency Node at the version in `.nvmrc`. `npm run check`
runs the drift check and the validator while authoring; `npm run quality`
is the gate that must pass before every push, and CI runs exactly it.

## Preview

- Single diagram: open its HTML file directly (`file://` works).
- Gallery: `python3 -m http.server 8000` in the repo root, then
  <http://localhost:8000/> (the manifest fetch needs HTTP).

## Updating consumers after diagram changes

The blog builds against a pinned figura commit. In the blog repo, run the
`/bump-figura` command: it moves the submodule pointer, runs the blog's
`npm run quality` gate, and reports what changed. The ai-experiments docs
site commits copies of the static diagrams; re-export them with
`node scripts/export-svg.js` and copy them there. Each manifest entry's
`consumers` list names who must pick a change up.
