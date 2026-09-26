---
description: Re-export the static diagrams and list the consumer copies each one replaces
---
Run `npm run export`, then `git diff --stat -- exports/`.

For each export that changed, read its manifest entry and list every `consumers` path that is a
copy of the image (an `.svg` path), with the command to replace it from a checkout of that
repository next to this one, for example:

```bash
cp exports/ai-experiments/tier-loop.svg ../ai-experiments/site/static/img/diagrams/tier-loop.svg
```

figura never writes to another repository: print the commands, and stop.
