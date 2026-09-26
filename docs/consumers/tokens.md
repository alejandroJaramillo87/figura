# Token contract

The contract between figura's design tokens and the two repositories that mirror some of their
values: which file is the source, who mirrors what, what checks each mirror, and how to change a
token without breaking a consumer.

## The source

`shared/tokens.css` is the source of every token value. Diagrams never link it:
`npm run build` stamps its values into each diagram's `palette-classic` block. The values and
their uses are in the [token table](../../.styles/DIAGRAM_STYLE.md#tokens), and what each hue
means is in the [authoring guide](../authoring/guide.md#palette-meaning).

## The mirrors

| Consumer | Mirror | Check |
|----------|--------|-------|
| curiosity-chronicles | Eleven values, for its code panels | `curiosity-chronicles/tests/check-figura-tokens.mjs`, in the blog's quality gate |
| ai-experiments | The same values, in `ai-experiments/site/src/css/custom.css` | None yet |

The blog owns its pair table, mapping each of its variables to the figura token it mirrors, in
[curiosity-chronicles/docs/diagrams/figura.md](https://github.com/alejandroJaramillo87/curiosity-chronicles/blob/main/docs/diagrams/figura.md).
Its check compares the mirror against the `shared/tokens.css` in its submodule, so a token
change here fails the blog's gate at the next submodule bump until the blog updates its mirror,
in the same commit as the bump.

ai-experiments has no such check, so its mirror can drift without anything failing. One
difference is already there: its `--font-mono` names a different font stack from figura's
`--fg-mono`. Whether that difference is deliberate is undecided.

## Changing a token

1. Edit the value in `shared/tokens.css`, keeping its trailing use comment accurate.
2. Run `npm run build`, which rewrites every diagram's palette block.
3. Run `npm run export`, because static exports carry the values too, then `npm run quality`.
4. In the pull request, name the consumer follow-ups: the blog updates its mirror when it bumps
   (see [blog.md](blog.md#release-flow)), and ai-experiments updates `custom.css` and re-copies
   any changed export (see [docs-site.md](docs-site.md)).
