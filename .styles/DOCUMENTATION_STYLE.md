# Documentation Style Guide

Standards for every markdown file that documents this repository: `docs/`, the router READMEs,
`AGENTS.md`, the style guides and the agent definitions under `.claude/`.

## Table of Contents

<!-- toc:start -->

1. [Document class](#document-class)
2. [Writing standards](#writing-standards)
3. [Document structure](#document-structure)
4. [README shape](#readme-shape)
5. [Formatting](#formatting)
6. [Cross-references](#cross-references)
7. [Prohibited](#prohibited)

<!-- toc:end -->

## Document class

Every document belongs to one of three classes. The class decides whether drift against the
current repository is a bug to fix or a record to preserve, so the document states it.

| Class | What it is | Obligation |
|-------|------------|------------|
| Living reference | Describes the tree as it is now | Correct it when the tree moves |
| Frozen record | What was decided or planned on a day | Never edit the body; drift is expected |
| Parked proposal | Work described but not scheduled | Dated at authoring; edited only as items graduate |

Living reference is the default and carries no marker. The other two declare themselves in a
single bold line under the H1, before the description paragraph, with an ISO date:

```markdown
# Removing the hero diagram kind

**Frozen record, 2026-08-29. Drift against the current repository is expected; this document
is never updated.**
```

A frozen record lives under an `investigations/` directory. The path is what the gates read:
`tests/check-links.mjs`, `tests/check-retired-names.mjs`, `tests/check-command-prompts.mjs` and
the table-of-contents generator all exempt `investigations/`, and nothing else. A frozen record
stored anywhere else is checked as though it were living.

## Writing standards

- **Active voice**: "The build rewrites the block", not "The block is rewritten by the build".
- **Present tense** for current state; **imperative mood** for instructions.
- One idea per sentence, one topic per paragraph; define a term before using it.
- State facts the tree can confirm, and name the file that owns each one. A count, a version or
  a path that belongs to another file is linked, not repeated: a fact stated in two places is a
  fact that will disagree with itself.

## Document structure

```markdown
# Title

Description paragraph. Its first sentence stands alone, because the parent README's generated
table quotes it.

## Table of Contents

<!-- toc:start -->
<!-- toc:end -->

## Main content
```

One H1 per document. A document over 500 words with four or more H2 and H3 headings carries
a table of contents, and the list is never written by hand: `npm run docs` renders it between
the markers from the headings, and adds the section when it is missing. `npm run quality`
fails a stale list. A README never carries one; a frozen record is never given one.

## README shape

Every tracked directory has a README, except hidden directories, `exports/` and the per-consumer
directories under `diagrams/`, which the catalog in `diagrams/README.md` covers. A README is
the directory's router, not a document:

1. The H1, then the description paragraph. Its first sentence stands alone.
2. The generated tables, directly after: `inventory:dirs` when the directory has
   subdirectories, `inventory:pages` when it has files, both when it has both.
3. Orientation a table cannot carry, in a few paragraphs at most: reading order, traps.

The tables are rendered by `npm run docs` from each entry's own description: a
subdirectory's README intro, a document's intro, a diagram's manifest `description`, or a code
file's header comment (see `COMMENT_STYLE.md`). An entry with no description of its own, such
as a runtime block, is described in the README with a comment the generator reads:

```markdown
<!-- describe caption-core.js: Sizes the caption box for its longest variant. -->
```

To change what a row says, change the entry's own first sentence and rerun `npm run docs`.
Editing the table directly is overwritten on the next run and fails the gate until then.

## Formatting

- **Bold** for emphasis; `backticks` for commands, paths, keys, block names and rule ids.
- Always tag a code block's language. A shell block carries no prompt: write the command
  exactly as the shell must receive it. A block that shows a command beside its output is
  tagged `console` and keeps the `$ ` prompt. `tests/check-command-prompts.mjs` enforces this.
- Pipe tables with headers; `-` for unordered lists, `1.` for ordered ones.
- Headings in sentence case ("Changing a shared token"); the generated `## Table of Contents`
  heading is the one exception. No H4: the table of contents lists H2 and H3 only, so an H4
  section drops out of it.
- Dates are ISO `YYYY-MM-DD`, always.

## Cross-references

Internal links are relative paths and must resolve: `tests/check-links.mjs` fails a broken one.
A repository path in backticks (`scripts/lib/fragment.js`) is written from the repository root
and must exist too; the same check resolves it. A path in another repository carries that
repository's name in front (`curiosity-chronicles/tests/quality.mjs`), or is a GitHub URL, so
it is never resolved here.
When a file is renamed, add the old path to `RETIRED` in `tests/check-retired-names.mjs`.

## Prohibited

- Emojis, decorative banners, exclamation marks.
- Marketing language and subjective adjectives ("easy", "powerful", "seamless").
- Contractions and rhetorical questions in reference documents.
