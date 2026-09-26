# Blog consumer

How the [Curiosity Chronicles](https://github.com/alejandroJaramillo87/curiosity-chronicles)
blog takes figura diagrams, seen from figura's side: the submodule pin, the build-time inlining
and the release flow. The blog documents its own side in
`curiosity-chronicles/docs/diagrams/figura.md`. Each manifest entry's `consumers` list names the
posts that embed it.

## The submodule

The blog mounts this repository as a git submodule at `curiosity-chronicles/static/diagrams`,
tracking branch `main`. The blog therefore builds against a pinned commit of figura, not the tip
of `main`: a push here changes nothing on the blog until its pointer moves.

## How a diagram reaches the page

The blog's shortcode, `curiosity-chronicles/layouts/shortcodes/diagram.html`, inlines a diagram
at build time, with no iframe and no runtime fetch:

1. A post writes `{{</* diagram name="<dir>/<name>" */>}}`.
2. Hugo reads `curiosity-chronicles/static/diagrams/diagrams/<dir>/<name>.html`, a file in this repository's
   `diagrams/` tree.
3. The shortcode keeps the region between `<!-- fg:embed-start -->` and
   `<!-- fg:embed-end -->` and discards the rest: the preview chrome, the `preview.css` link and
   the page title.
4. It wraps the fragment in `<figure class="fg-figure">`, adds `fg-figure--wide` for
   `wide=true`, and adds a `<figcaption>` rendered from the `caption` parameter.

The shortcode fails the blog build when `name` is missing, when the file does not exist (a typo,
or an uninitialized submodule), or when either embed marker is missing. The markers are
therefore load-bearing: a file without `fg:embed-end` would otherwise inline the rest of the
page.

Figure framing, the wide breakout and the "Figure N." caption numbering are styled on the blog
side; the fragment carries none of them. The directory under `diagrams/` is a convention for
humans (see [the naming rule](../../.styles/DIAGRAM_STYLE.md#workflow-for-a-new-diagram)); the
shortcode resolves whatever path `name` gives it.

## Why inlining shapes the rules

Build-time inlining puts the fragment verbatim into a page full of other CSS, JS and possibly
other figura diagrams, including a second copy of itself. Each
[hard rule](../../.styles/DIAGRAM_STYLE.md#hard-rules) answers a failure of that setup: an
unscoped selector restyles the post, a shared id resolves to another diagram's definition, a
script that looks up its root globally drives the wrong copy, an external request breaks the
blog's promise of no third-party requests, and a caption that grows reflows the text around it.
The gallery's duplicated first entry, and the browser tier of the
[quality gate](../testing/quality-gate.md), exercise the same conditions here.

## Release flow

1. Change diagrams here, and pass `npm run quality` (plus `npm run quality:full` for a change a
   reader can see).
2. Merge to `main`, where CI runs the same gate.
3. In the blog repository, run its `/bump-figura` command. It moves the submodule pointer, runs
   the blog's own `npm run quality` and reports what changed; its steps are the blog's to
   define.

Until the blog bumps, it keeps building against the old commit. A breaking change here never
breaks the blog retroactively; it can only surface at bump time. A change to a shared token
also needs a follow-up on the blog side, described in [tokens.md](tokens.md).
