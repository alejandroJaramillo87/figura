# Comment style guide

Comment standards for every file type in this repository: the CommonJS scripts, the ESM checks,
CSS, the diagram HTML and the shared runtime blocks. Clarity over decoration, technical
precision, professional tone.

Comments explain **why** (intent, the chosen approach), give **context** the code does not show,
and give **maintenance guidance**. They do not restate what the code already says.

## Table of Contents

<!-- toc:start -->

1. [File headers](#file-headers)
2. [Syntax by file type](#syntax-by-file-type)
3. [Inline and block comments](#inline-and-block-comments)
4. [Status comments](#status-comments)
5. [What to avoid](#what-to-avoid)

<!-- toc:end -->

## File headers

Every script, check, stylesheet and snippet file opens with a header comment. Its first sentence
states what the file is for, in one line a reader can act on, because `tests/docs.mjs` lifts that
sentence into the parent directory's README table.

- Write the first sentence as a description of the file's role, not its name or its history:
  "Re-expands every managed block from its canonical source", not "build.js: the build script".
- Put usage, invariants and traps in the sentences after the first.
- Two kinds of file cannot carry a header, and are described in their directory README with a
  `<!-- describe NAME: ... -->` line instead. A runtime block under `shared/runtime/` is stamped
  verbatim into every diagram, so a header would ship in all of them. A diagram or template is
  an HTML page whose fragment ships verbatim, and its description lives in `manifest.json`.

## Syntax by file type

```js
// ESM checks under tests/: line comments.
```

```js
/*
 * CommonJS scripts under scripts/: a block comment for the header and for a
 * mechanism that spans several lines; line comments for a single statement.
 */
```

```css
/* CSS, including a diagram's <style>: block comments only. */
.fg-kv-cache-fill .cell { transition: fill var(--dur-fast) var(--ease); }
```

A diagram fragment carries **no HTML comments**, because the blog inlines it verbatim and every
comment ships to readers. Explain markup in the fragment's `<style>`, or in the commit message.
Outside the fragment, in a diagram page's `<head>`, a comment is harmless but still unneeded.

## Inline and block comments

- Inline comments explain a non-obvious value: `const PAD = 16; // matches the root padding`.
- Block comments explain a mechanism or a constraint that spans several lines.
- A comment that records a measured effect states the measurement, not an impression.

## Status comments

Use a consistent prefix and enough context to act on it:

```js
// TODO: Drop the fallback once every entry carries a kind.
// NOTE: The first IntersectionObserver callback reports any overlap as intersecting.
```

## What to avoid

- Decorative banners (`/* ==== EFFECTS ==== */`) and ASCII rules; a section header is a plain
  comment.
- Shouting prefixes such as `IMPORTANT:` or `NEVER`; state the constraint and its reason.
- Comments that restate the code, or that describe what the code used to do.
- Marketing language ("blazingly fast", "beautiful"). State the technical effect.
