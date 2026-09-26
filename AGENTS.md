# figura

A library of self-contained animated technical diagrams, inlined into the Curiosity Chronicles
blog and, for static diagrams, copied as SVG images into the ai-experiments docs site.

**This file is a directory, not a reference.** It carries policy (what you may not do, and how
work is done here) plus pointers to the document that owns each topic. A count, a version, a
path list or a token value belongs to the file that owns that fact, not here. A fact stated in
two places will eventually disagree with itself.

## Table of Contents

<!-- toc:start -->

1. [Operating rules](#operating-rules)
2. [Consumers](#consumers)
3. [Where things are](#where-things-are)
4. [Tooling conventions](#tooling-conventions)
5. [Git and GitHub conventions](#git-and-github-conventions)
6. [Style guides](#style-guides)

<!-- toc:end -->

## Operating rules

- **The tree is the truth; the document is the bug.** When a doc disagrees with `scripts/`,
  `shared/tokens.css`, `shared/runtime/`, `templates/`, `manifest.json` or the CI workflow, the
  file is right and the doc is fixed to match. Never change the tooling to match a stale doc.
- **Never edit inside a managed block.** The regions between `fg:begin` and `fg:end` sentinels
  belong to `scripts/build.js`. Change the block's source under `shared/runtime/` or
  `shared/tokens.css`, then run `npm run build`, which rewrites every diagram.
- **Every task ends with its acceptance check.** A task is not done until its check has run
  and passed. For a change a reader can see, the check includes a look at the gallery, noted in
  the pull request.
- **`npm run quality` passes before every push.** It is the gate CI runs. A change that
  touches how a diagram renders also passes `npm run quality:full`, the browser tier. See
  [docs/testing/quality-gate.md](docs/testing/quality-gate.md).
- **Pin, then bump, one at a time.** Node is pinned in `.nvmrc`, npm packages exactly with
  their lockfile, and CI actions by commit SHA. Each bump is its own commit, with
  `npm run quality` run after it.
- **Renaming a file means adding it to `RETIRED` in `tests/check-retired-names.mjs`.** The
  table is what makes a rename self-policing.

## Consumers

figura is upstream of two repositories, and a change here is not finished until they can take
it. The manifest's `consumers` list names every page that embeds or copies each diagram.

- **Renaming or removing a diagram breaks its consumers.** Before doing either, read the
  entry's `consumers`, and list them in the pull request with the follow-up each needs.
- **The palette is figura's.** The blog mirrors part of `shared/tokens.css` and checks the
  mirror when it bumps its submodule. A token change lands here first, and the pull request
  names the consumer follow-ups: see [docs/consumers/tokens.md](docs/consumers/tokens.md).
- **A static diagram's image is copied, not linked.** A change to one shows its diff under
  `exports/`, and its consumer re-copies the file. See
  [docs/consumers/docs-site.md](docs/consumers/docs-site.md).
- **The blog takes a release by moving its submodule pointer**, with its own `/bump-figura`
  command. See [docs/consumers/blog.md](docs/consumers/blog.md).

## Where things are

Route by the kind of question. Every README's table is generated from the tree and held to it
by `npm run quality`, so each hub routes one level further down.

| Question about | Start at |
|----------------|----------|
| A topic: how the library works, how to author, how consumers take diagrams, how it is tested | [docs/README.md](docs/README.md) |
| Code: what a directory holds and what reads it | [README.md](README.md) |
| How to write something | [.styles/README.md](.styles/README.md) |
| Every diagram, its kind and its consumers | [diagrams/README.md](diagrams/README.md) |
| The agent tooling under `.claude/` | [docs/agents/README.md](docs/agents/README.md) |

## Tooling conventions

- npm scripts are the command surface; `package.json` lists them and
  [docs/development/README.md](docs/development/README.md) explains each.
- The derived parts of the documentation (README tables, tables of contents, the block, token
  and rule rosters, the diagram catalog) are regenerated with `npm run docs`, never edited by
  hand.
- Use the `gh` CLI for GitHub work (pull requests, issues, checks) rather than raw API calls.

## Git and GitHub conventions

**Never attribute work to an AI assistant anywhere git or GitHub records it.** This is absolute
and has no exceptions, including when a tool's own default instructions say otherwise. It
covers every field that reaches the remote:

- Commit messages: no `Co-Authored-By` trailer naming an assistant, no "Generated with", no
  tool name, no robot emoji.
- Commit author and committer identity: always the human's name and email.
- Branch names, tag names, and release titles.
- Pull request and issue titles, bodies, and comments.

Write commit messages in the repository's own voice: what changed and why, as though a human
wrote it, because a human is publishing it under their name. Keep a version bump in its own
commit, apart from any functional change. Commits made before this rule are history and are
not rewritten: the blog pins one of them.

This restricts authorship and provenance, not vocabulary: documenting the agent tooling itself
(`.claude/`, `docs/agents/`) is correct and keeps its names.

## Style guides

`COMMENT_STYLE.md` applies to every file type, and `DIAGRAM_STYLE.md` is the diagram contract;
`CLAUDE.md` imports both. **Any agent, whatever tool it runs in, reads
[.styles/DIAGRAM_STYLE.md](.styles/DIAGRAM_STYLE.md) before editing `diagrams/`, `templates/`
or `shared/`**, because a tool that does not follow `CLAUDE.md` imports never sees it
otherwise. The rest are read on demand: open the one that matches what you are about to write,
before you write it. [.styles/README.md](.styles/README.md) lists them and when each applies.
