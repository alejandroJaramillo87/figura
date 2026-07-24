# figura

A growing library of animated, interactive technical diagrams — SVG + CSS +
vanilla JS, one self-contained HTML file per diagram — for the
[Curiosity Chronicles](https://alejandrojaramillo87.github.io/curiosity-chronicles/)
blog (LLM internals, mech interp, inference engines).

## How it works

- Each diagram is a standalone HTML page you can open directly in a browser.
  The portion between `<!-- fg:embed-start -->` / `<!-- fg:embed-end -->` is a
  fully self-contained fragment (scoped styles, namespaced SVG ids, IIFE JS).
- The blog mounts this repo as a git submodule at `static/diagrams` and a Hugo
  shortcode inlines the fragment at build time — no iframes, no runtime deps:

  ```
  {{</* diagram name="inference-loop/kv-cache-fill" caption="The KV cache during decode." */>}}
  ```

- Diagrams are authored by a coding agent from diagram notes, following the
  contract in [CLAUDE.md](CLAUDE.md) and using existing diagrams as style
  reference — the library grows organically with each post.

## Layout

```
CLAUDE.md        generation contract (conventions, palette, patterns)
index.html       gallery — every diagram inlined, first one twice (collision check)
manifest.json    diagram index {id, path, title, post, description}
shared/
  tokens.css     palette source of truth: classic dark, pastel-on-dark,
                 pastel-light (build.js derives the per-diagram palette blocks)
  runtime/       canonical managed-block sources (timeline, controls bar,
                 caption box, panel base, reduced-motion) stamped into every
                 fragment by scripts/build.js
  effects.css    effects catalog: glow, sweep, comet, draw-in, ripple,
                 shimmer, flash (copy-source patterns)
  snippets.js    reference JS patterns (documentation; runtime/ is executable)
  preview.css    page chrome for standalone/gallery viewing only
scripts/
  new-diagram.js scaffold a diagram from templates/ with blocks pre-expanded
  build.js       re-expand managed blocks (--check fails on drift)
  validate.js    contract linter: scoping, id prefixes, reduced motion,
                 a11y, self-containment, manifest sync
templates/       step-timeline, hover-inspect, ambient scaffolds
diagrams/<post-slug>/<kebab-name>.html
```

Tooling is zero-dependency Node (>= 18): `npm run check` runs the drift
check and the validator; CI runs the same on every push and pull request.

## Preview

- Single diagram: open its HTML file directly (`file://` works).
- Gallery: `python3 -m http.server 8000` in the repo root, then
  <http://localhost:8000/> (the manifest fetch needs HTTP).

## Updating the blog after diagram changes

In the blog repo: `git submodule update --remote static/diagrams`,
`git add static/diagrams`, commit, push. Posts pick up the new pinned commit
on the next build.
