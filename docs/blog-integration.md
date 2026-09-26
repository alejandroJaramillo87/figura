# Blog integration (Curiosity Chronicles)

figura has two consumers. The
[Curiosity Chronicles](https://github.com/alejandroJaramillo87/curiosity-chronicles)
blog inlines diagrams into posts, which this doc covers from figura's
side; the blog-side view lives in the blog repo at
`curiosity-chronicles/docs/diagrams/figura.md`. The ai-experiments docs site commits copies of
the static diagrams' SVG exports (see
[architecture.md](architecture.md#the-scripts-pipeline)). Each manifest
entry's `consumers` list names the pages that use it.

## The submodule

The blog mounts this repo as a git submodule at `static/diagrams`
(branch `main`). The blog therefore builds against a **pinned commit**
of figura, not the tip of `main` — pushing changes here does nothing
visible on the blog until the pointer is bumped (see the release flow
below).

## How diagrams reach the page

The blog's Hugo shortcode `layouts/shortcodes/diagram.html` inlines a
diagram at **build time** — no iframe, no runtime fetch:

1. A post writes `{{</* diagram name="<dir>/<name>" */>}}`.
2. Hugo reads `static/diagrams/diagrams/<dir>/<name>.html`
   (i.e. a file in this repo's `diagrams/` tree).
3. It extracts the region between `<!-- fg:embed-start -->` and
   `<!-- fg:embed-end -->` — everything outside the markers (preview
   chrome, `preview.css` link, page title) is discarded.
4. The fragment is wrapped in `<figure class="fg-figure">`, with
   `fg-figure--wide` added for `wide=true` and an optional
   markdownified `<figcaption>` from the `caption` param.

The shortcode fails the blog build with a clear error when the `name`
param is missing, when the diagram file does not exist (typo, or an
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
2. Merge to `main` (CI runs the same check).
3. In the blog repo, run the `/bump-figura` command. It moves the
   submodule pointer, runs the blog's `npm run quality` gate (which
   includes its mirrored-token check), and reports what changed. A
   bump is its own commit there.
4. Push; the blog rebuilds against the new pin.

Until step 3 lands, the blog keeps building against the old commit —
which also means a breaking change here never breaks the blog
retroactively; it can only break at bump time.

## Shared design language

The integration is visual as well as mechanical:

- `shared/tokens.css` is the source of truth. The blog mirrors eleven
  of its values as its dark-panel tokens in `assets/scss/custom.scss`,
  and the blog's `curiosity-chronicles/tests/check-figura-tokens.mjs` fails until the mirror
  matches. A palette change therefore lands here first, and the blog
  updates its mirror in the same commit as the bump that brings it in.
- Diagrams **never theme-switch**: the dark slate panel reads as a
  framed figure on the blog's light theme and sits nearly flush on its
  dark theme. The blog styles its code panels from the same material,
  so diagrams and code read as one system.
- Figure framing, breakout width, and automatic "Figure N." caption
  numbering live blog-side (`.fg-figure`, `.fg-figure--wide`,
  `.fg-figcaption` in `custom.scss`) — the fragment itself carries
  none of that.

## Naming convention

`diagrams/<dir>/` names where a diagram is used: a blog post's
filename stem, the series directory for a post in a series
(`what-language-leaves-out/`), or a docs-site section for a static
diagram (`rust-harness/`). The manifest's `consumers` field records the
exact pages. The directory is a convention for humans, not something the
shortcode depends on: it resolves whatever path `name` gives it.
