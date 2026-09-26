# Docs-site consumer

How the ai-experiments docs site takes figura's static diagrams: it copies each exported SVG
into its own tree and references the copy as an image. The site cannot inline HTML or run
script, which is why the `static` kind and `scripts/export-svg.js` exist (see
[static exports](../architecture/overview.md#static-exports)).

## The copy

Each static diagram exports to `exports/<slug>/<id>.svg`, committed in this repository. The
docs site copies it to `ai-experiments/site/static/img/diagrams/<id>.svg`. The destination is
flat, which is safe because manifest ids are unique. The site's docs pages then reference the
copy as an image.

The manifest entry's `consumers` list names both sides of that: the copied file and every page
that shows it, each as `ai-experiments:<path>`. Read that list before renaming, removing or
changing a static diagram.

## Changing a static diagram

1. Edit the diagram's HTML under `diagrams/`, never the export.
2. Run `npm run export`, and commit the changed file under `exports/` in the same pull request.
   The image diff there is the reviewable change; the quality gate's `exports` step fails while
   an export is stale.
3. In the pull request, name the follow-up: ai-experiments re-copies the file to each path its
   `consumers` entry lists.

## Never edit the copy

The copy in ai-experiments is an output, not a source. A hand edit there is undone by the next
re-copy, silently.

This has happened. On 2026-09-18 a hand edit to `ai-experiments/site/static/img/diagrams/tier-loop.svg`
changed "train, distill" to "train, fine-tune". The wording was right, so the change was made
again in figura's source, `diagrams/ai-experiments/tier-loop.html`, and re-exported. Had it
stayed only in the copy, the next re-copy would have reverted it. A wording change to a diagram is a figura change.

## The consumer's side of the contract

figura holds its half: the committed export is current, and `node scripts/export-svg.js --check`
proves it. Nothing yet proves the other half, that each copy in ai-experiments matches a figura
export. ai-experiments should keep a provenance record for its copies, naming for each file the
figura commit it came from and its sha256, and check that record in its own quality gate. A copy
whose hash no longer matches the record is then a hand edit, caught before it lands.
