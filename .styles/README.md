# Style guides

Style guides for every kind of file in this repository, read before writing that kind of file.
`CLAUDE.md` imports `COMMENT_STYLE.md`, which applies everywhere, and `DIAGRAM_STYLE.md`, the
diagram contract, into every agent session; the rest are read on demand.

<!-- inventory:guides:start -->

| Guide | Governs |
|-------|---------|
| [COMMENT_STYLE.md](COMMENT_STYLE.md) | Comment standards for every file type in this repository: the CommonJS scripts, the ESM checks, CSS, the diagram HTML and the shared runtime blocks. |
| [DIAGRAM_STYLE.md](DIAGRAM_STYLE.md) | The contract every diagram, template and shared runtime file in this repository follows: how a diagram is made, what its fragment may contain, and which check holds each rule. |
| [DOCUMENTATION_STYLE.md](DOCUMENTATION_STYLE.md) | Standards for every markdown file that documents this repository: `docs/`, the router READMEs, `AGENTS.md`, the style guides and the agent definitions under `.claude/`. |

<!-- inventory:guides:end -->

`DIAGRAM_STYLE.md` is imported although it governs one kind of file, because nearly every change
here touches a diagram, a template or `shared/`, and an unread contract is an unfollowed one.
