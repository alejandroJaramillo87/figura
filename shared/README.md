# Shared

The sources every diagram draws from: the design tokens, the managed-block runtime, the effects
catalog and the copy-source helpers.

<!-- inventory:dirs:start -->

| Directory | Holds |
|-----------|-------|
| [runtime/](runtime/README.md) | The canonical source of every managed block that `scripts/build.js` stamps into diagrams between `fg:begin` and `fg:end` sentinels. |

<!-- inventory:dirs:end -->

<!-- inventory:pages:start -->

| File | Holds |
|------|-------|
| [effects.css](effects.css) | The effects catalog: copy-source animation patterns for figura diagrams. |
| [preview.css](preview.css) | Page chrome for viewing diagrams standalone or in the gallery. |
| [snippets.js](snippets.js) | Copy-source helpers for step-triggered effects. |
| [tokens.css](tokens.css) | The design tokens for every figura diagram, and their source of truth. |

<!-- inventory:pages:end -->

Nothing here is linked from a diagram's fragment. `tokens.css` and `runtime/` are stamped into
each diagram by `npm run build`; `effects.css` and `snippets.js` are copied from by hand; and
`preview.css` styles only the standalone page around a fragment.
