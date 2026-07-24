# Blog integration (Curiosity Chronicles)

figura exists to serve one consumer: the
[Curiosity Chronicles](https://github.com/alejandroJaramillo87/curiosity-chronicles)
blog. This doc covers the mechanics of that integration from figura's
side; the blog-side view lives in the blog repo at
`docs/diagrams-figura.md`.

## The submodule

The blog mounts this repo as a git submodule at `static/diagrams`
(branch `main`). The blog therefore builds against a **pinned commit**
of figura, not the tip of `main` — pushing changes here does nothing
visible on the blog until the pointer is bumped (see the release flow
below).

## How diagrams reach the page

The blog's Hugo shortcode `layouts/shortcodes/diagram.html` inlines a
diagram at **build time** — no iframe, no runtime fetch:

1. A post writes `{{</* diagram name="<post-slug>/<name>" */>}}`.
2. Hugo reads `static/diagrams/diagrams/<name>.html` (i.e. a file in
   this repo's `diagrams/` tree).
3. It extracts the region between `<!-- fg:embed-start -->` and
   `<!-- fg:embed-end -->` — everything outside the markers (preview
   chrome, `preview.css` link, page title) is discarded.
4. The fragment is wrapped in `<figure class="fg-figure">`, with
   `fg-figure--wide` added for `wide=true` and an optional
   markdownified `<figcaption>` from the `caption` param.

The shortcode fails the blog build with a clear error when the `name`
param is missing, when the diagram file doesn't exist (typo, or an
uninitialized submodule), or when the file lacks the
`fg:embed-start` marker — so the embed markers are load-bearing, not
decorative.

## Why the hard rules exist

Build-time inlining means the fragment lands verbatim in a page full
of other CSS, JS, and possibly other figura diagrams — including a
second copy of itself. Each hard rule in [CLAUDE.md](../CLAUDE.md)
maps to a failure mode of that setup:

- **CSS scoping / keyframe prefixes** — unscoped selectors or generic
  keyframe names would restyle the blog or another diagram.
- **Namespaced SVG ids** — ids become document-global once inlined;
  duplicate ids across diagrams would make markers/gradients resolve
  to the wrong definition.
- **Scoped IIFE JS via `document.currentScript.closest()`** — the only
  root-resolution strategy that stays correct when the same fragment
  appears twice on a page.
- **No external requests** — the blog ships with zero third-party
  requests; a webfont or CDN script in a fragment would break that.
- **No layout shift** — a hover caption that grows on interaction
  would reflow the surrounding post text.

The gallery (`index.html`) rendering the first manifest entry twice is
the standing regression check for the multi-instance case.

## Release flow

1. Author or change diagrams here; pass `npm run check`.
2. Merge/push to `main` (CI runs the same check).
3. In the blog repo, bump the submodule pointer:

   ```bash
   git submodule update --remote static/diagrams
   git add static/diagrams
   git commit -m "Bump figura diagrams"
   ```

4. Push; the blog rebuilds against the new pin.

Until step 3 lands, the blog keeps building against the old commit —
which also means a breaking change here never breaks the blog
retroactively; it can only break at bump time.

## Shared design language

The integration is visual as well as mechanical:

- `shared/tokens.css` is the diagram-side counterpart of the blog's
  design tokens in `assets/scss/custom.scss` — same slate neutrals,
  same sky `#38bdf8` accent, same radii/motion/type values. A palette
  change should be considered on both sides.
- Diagrams **never theme-switch**: the dark slate panel reads as a
  framed figure on the blog's light theme and sits nearly flush on its
  dark theme. The blog styles its code panels from the same material,
  so diagrams and code read as one system.
- Figure framing, breakout width, and automatic "Figure N." caption
  numbering live blog-side (`.fg-figure`, `.fg-figure--wide`,
  `.fg-figcaption` in `custom.scss`) — the fragment itself carries
  none of that.

## Naming convention

`diagrams/<post-slug>/` matches the blog post's filename stem under
the blog's `content/posts/`, and the manifest's `post` field records
which post each diagram belongs to (with placeholder values for posts
not yet written). This is a convention for humans, not something the
shortcode depends on — it resolves whatever path `name` gives it.
