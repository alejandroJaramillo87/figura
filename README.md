# figura

A library of animated, interactive technical diagrams, each one self-contained HTML file of SVG,
scoped CSS and vanilla JS, for the
[Curiosity Chronicles](https://alejandrojaramillo87.github.io/curiosity-chronicles/) blog, with
static diagrams also exported as SVG images for the ai-experiments docs site.

<!-- describe .github: The CI workflow, which runs the quality gate and the browser tier. -->
<!-- describe .styles: Style guides, including the diagram contract every diagram follows. -->
<!-- describe .claude: Agent definitions, commands and permission settings for Claude Code sessions. -->
<!-- describe exports: Committed SVG images of the static diagrams, held to their sources by export --check. -->

<!-- inventory:dirs:start -->

| Directory | Holds |
|-----------|-------|
| [.claude/](.claude/README.md) | Agent definitions, commands and permission settings for Claude Code sessions. |
| [.github/](.github/) | The CI workflow, which runs the quality gate and the browser tier. |
| [.styles/](.styles/README.md) | Style guides, including the diagram contract every diagram follows. |
| [diagrams/](diagrams/README.md) | Every diagram in the library, one directory per consumer location: a blog post's filename stem, a series directory, or a docs-site section. |
| [docs/](docs/README.md) | How figura works and how to work in it, one directory per topic; the diagram contract itself is .styles/DIAGRAM_STYLE.md. |
| [exports/](exports/) | Committed SVG images of the static diagrams, held to their sources by export --check. |
| [scripts/](scripts/README.md) | The command-line tools that scaffold, build, validate and export diagrams, all CommonJS on Node built-ins, run through the npm scripts in `package.json`. |
| [shared/](shared/README.md) | The sources every diagram draws from: the design tokens, the managed-block runtime, the effects catalog and the copy-source helpers. |
| [templates/](templates/README.md) | One scaffold per diagram kind, which `scripts/new-diagram.js` copies to start a new diagram. |
| [tests/](tests/README.md) | The quality gate and the checks it runs, beyond the validator in `scripts/`: retired names, code blocks, links, contract citations, generated docs and the browser tier. |

<!-- inventory:dirs:end -->

Start with [AGENTS.md](AGENTS.md) for the operating rules and where each topic lives, and
[.styles/DIAGRAM_STYLE.md](.styles/DIAGRAM_STYLE.md) before writing a diagram. The files at the
top level:

| File | Holds |
|------|-------|
| `index.html` | The gallery: every diagram inlined the way the blog inlines it, the first one twice |
| `manifest.json` | One entry per diagram: `id`, `path`, `title`, `kind`, `consumers`, `description` |
| `package.json` | The npm scripts, which are the command surface |
| `.nvmrc` | The exact Node version the gate and CI run |

## How it works

Each diagram is a standalone HTML page you can open in a browser. The part between
`<!-- fg:embed-start -->` and `<!-- fg:embed-end -->` is a self-contained fragment, and the blog
mounts this repository as a submodule and inlines that fragment into posts through a Hugo
shortcode, with no iframe and no runtime dependency:

```text
{{</* diagram name="inference-loop/kv-cache-fill" caption="The KV cache during decode." */>}}
```

## Commands

```bash
npm run check          # while authoring: managed-block drift and the validator
npm run quality        # before every push; CI runs exactly this
npm ci && npm run quality:full   # adds the browser tier
npm run docs           # regenerate README tables, tables of contents and rosters
```

To preview the gallery, serve the repository (`python3 -m http.server 8000`) and open
<http://localhost:8000/>; the manifest fetch needs HTTP. A single diagram opens directly from
disk.
