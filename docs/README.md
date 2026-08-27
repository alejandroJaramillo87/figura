# Documentation

Project documentation for figura. These docs are the human-oriented
explanation of how the library works and why; the terse, enforced
generation contract that diagram authors (human or agent) must follow
lives in the repo root's [CLAUDE.md](../CLAUDE.md).

- [architecture.md](architecture.md) — how the repo is coded: the
  one-file-per-diagram model, the embed fragment, the managed-blocks
  system, the scripts pipeline, `manifest.json`, and the gallery.
- [blog-integration.md](blog-integration.md) — how figura plugs into
  the Curiosity Chronicles blog: the git submodule, the Hugo `diagram`
  shortcode, the release/bump flow, and the shared design language.
- [development.md](development.md) — creating, editing, checking, and
  previewing diagrams; the CI pipeline; troubleshooting validator and
  drift-check failures.
- [authoring.md](authoring.md) — the visual language: palette
  semantics, the effects catalog, interaction kinds, accessibility and
  motion rules, and taste guidelines.
- [hero-art-direction.md](hero-art-direction.md) — choosing an art
  *treatment* for a hero: the vocabulary, why a style fits a subject or
  fails it, the five candidate treatments and what each costs to build
  here. Judgment, not enforcement.

See also the repo root: [README.md](../README.md) (quick start) and
[CLAUDE.md](../CLAUDE.md) (the generation contract).
