# Agent tooling

The agents, commands and settings under `.claude/`, what each is for, and which to reach for.
Every one of them works inside the diagram contract in
[../../.styles/DIAGRAM_STYLE.md](../../.styles/DIAGRAM_STYLE.md), which
[../../AGENTS.md](../../AGENTS.md) makes mandatory reading for any agent, whatever tool it runs in.

## Table of Contents

<!-- toc:start -->

1. [Agents](#agents)
2. [Commands](#commands)
3. [Settings](#settings)
4. [Which to reach for](#which-to-reach-for)

<!-- toc:end -->

## Agents

Each agent is a markdown file under `.claude/agents/` with its tools, model and description in
the front matter, which the table below is generated from. Detection and repair are separate
roles, so an agent that reports cannot also rewrite what it reports on: doc-auditor and
doc-writer split the documentation, and diagram-auditor and diagram-author split the diagrams.

<!-- inventory:agents:start -->

| Agent | Tools | Role |
|-------|-------|------|
| `diagram-auditor` | Read, Grep, Glob, Bash | Diagram contract auditor. Invoke to check diagrams against the rules the validator cannot see, and their labels against the facts of the pages that use them. Reports findings only; use diagram-author to fix them. |
| `diagram-author` | Read, Grep, Glob, Edit, Write, Bash | Writes and repairs diagrams under diagrams/ from the author's diagram notes or an auditor's findings, following .styles/DIAGRAM_STYLE.md. Invoke for new diagrams, diagram fixes, templates and shared runtime changes. |
| `doc-auditor` | Read, Grep, Glob, Bash | Documentation drift detector. Invoke to check documented commands, paths, block names, tokens, rules and behavior against the actual tree and report every mismatch. Reports drift only; use doc-writer to repair it. |
| `doc-writer` | Read, Grep, Glob, Edit, Write, Bash | Writes and updates repository documentation following the .styles guides. Invoke for docs/, READMEs, style guides and AGENTS.md. Never for diagrams. |
| `skeptic` | Read, Grep, Glob, Bash | Adversarial verifier. Invoke to independently check whether a claim, or a task marked done, actually holds. Returns CONFIRMED or REFUTED with evidence. |

<!-- inventory:agents:end -->

## Commands

Commands are prompts under `.claude/commands/`, invoked as `/name`; the table is generated from
their front matter.

<!-- inventory:commands:start -->

| Command | Does |
|---------|------|
| `/audit-diagram <diagrams/slug or path>` | Audit diagrams against the review-only contract rules and their consumer pages |
| `/audit-docs <docs-path>` | Audit a docs subtree against the tree and return a drift list |
| `/export-static` | Re-export the static diagrams and list the consumer copies each one replaces |
| `/new-diagram <consumer-dir>/<kebab-name> <kind>` | Scaffold, author and gate a new diagram from the author's notes, then stop for review |

<!-- inventory:commands:end -->

## Settings

`.claude/settings.json` allows the gate and generator commands without a prompt (`npm run
check`, `npm run quality`, `npm run docs`, `npm run build`, `npm run export`, `node scripts/...`,
`node tests/...`, read-only git), and asks before `git push`, before any other web fetch, and
before an edit to `shared/tokens.css`, which two other repositories mirror. It denies edits
under `exports/`, which only `npm run export` writes. Managed blocks cannot be protected by
path, so `build --check` in the gate is their guard.

## Which to reach for

- A new diagram from the author's notes: `/new-diagram`, which stops for review before any
  commit.
- A diagram that might break a review-only rule, or disagree with its page: `/audit-diagram`,
  then `diagram-author` for the fixes.
- A static diagram changed: `/export-static` for the copy commands its consumers need.
- A doc might be wrong: `/audit-docs`, then `doc-writer` for the fixes.
- A result someone reports as done: `skeptic`.
