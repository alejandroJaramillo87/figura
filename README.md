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
  tokens.css     reference palettes/tokens: classic dark, pastel-on-dark,
                 pastel-light (copied into diagrams, never linked)
  effects.css    effects catalog: glow, sweep, comet, draw-in, ripple,
                 shimmer, flash (copy-source patterns)
  snippets.js    reference JS patterns (timeline, controls, autoplay, hover,
                 effect restart, comet launch)
  preview.css    page chrome for standalone/gallery viewing only
diagrams/<post-slug>/<kebab-name>.html
```

## Preview

- Single diagram: open its HTML file directly (`file://` works).
- Gallery: `python3 -m http.server 8000` in the repo root, then
  <http://localhost:8000/> (the manifest fetch needs HTTP).

## Updating the blog after diagram changes

In the blog repo: `git submodule update --remote static/diagrams`,
`git add static/diagrams`, commit, push. Posts pick up the new pinned commit
on the next build.
