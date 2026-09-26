# Documentation

How figura works and how to work in it, one directory per topic; the diagram contract itself is
[.styles/DIAGRAM_STYLE.md](../.styles/DIAGRAM_STYLE.md).

<!-- inventory:dirs:start -->

| Directory | Holds |
|-----------|-------|
| [agents/](agents/README.md) | How agents work in this repository: the tooling under `.claude/` and the contract it works within. |
| [architecture/](architecture/README.md) | How the library is built: the fragment, the managed blocks, the scripts pipeline and the checks that hold it together. |
| [authoring/](authoring/README.md) | How to design a diagram that explains: choosing a kind, what the palette hues mean, and effect taste, which no check can judge. |
| [consumers/](consumers/README.md) | How the two repositories that use figura take its diagrams and its palette, and what a change here owes each of them. |
| [development/](development/README.md) | Setting up, the day-to-day commands, previewing, CI and troubleshooting. |
| [testing/](testing/README.md) | What the quality gate checks, how each tier runs, and how to read a failure. |

<!-- inventory:dirs:end -->

Read [architecture/](architecture/README.md) for the mechanism, [authoring/](authoring/README.md)
before a first diagram, and [consumers/](consumers/README.md) before changing a token, renaming
a diagram or touching a static one.
