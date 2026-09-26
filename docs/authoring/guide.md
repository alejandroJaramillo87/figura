# Authoring guide

The judgment calls that make a diagram look and behave like the rest of the library: which kind
to pick, what each hue means, and which effect earns its place. The mechanical rules live in
[.styles/DIAGRAM_STYLE.md](../../.styles/DIAGRAM_STYLE.md) and the validator enforces most of
them; this guide covers what no check can see. The live reference for every swatch and effect is
`diagrams/effects-sampler/effects-sampler.html`.

## Table of Contents

<!-- toc:start -->

1. [Choosing a kind](#choosing-a-kind)
2. [Palette meaning](#palette-meaning)
3. [Effects](#effects)
   - [Taste](#taste)
4. [Accessibility and motion](#accessibility-and-motion)
5. [Before you start](#before-you-start)

<!-- toc:end -->

## Choosing a kind

| Kind | Pick it when | Reader interaction |
|------|--------------|--------------------|
| `step-timeline` | A process unfolds over discrete steps: loops, cache fills, pipelines | Prev, play and next controls; autoplay once the diagram is in view |
| `hover-inspect` | An architecture or block diagram whose parts need explanation | Hovering or focusing a block fills the caption box |
| `toggle` | Two or a few readings of the same thing, compared by switching | A button cycles the states, or one button per state selects it |
| `ambient` | Continuous flow with no natural steps | None; a looping animation such as dashed-line flow |
| `static` | A reference figure read at a glance, for a consumer that cannot run script | None; state is encoded with hue, and the file exports as an SVG image |

Kinds compose (a step timeline can also carry hover captions), but start from the template
closest to the primary interaction. How each pattern is wired is in
[DIAGRAM_STYLE.md](../../.styles/DIAGRAM_STYLE.md#interaction-patterns).

## Palette meaning

The values live in the [token table](../../.styles/DIAGRAM_STYLE.md#tokens). The hues carry
meaning, and consistent use lets a reader carry intuition from one diagram to the next:

- `--accent` (sky): the thing happening now, such as active flow or the element the current
  step is about.
- `--ok` (green): settled state, such as filled, cached, residual or done.
- `--warn` (amber): work in flight or the hot path, such as decode.
- `--hot` (red): trouble, such as a bottleneck, an eviction or contention.
- `--violet`: a second series when one hue is not enough.
- The `-dim` variants: the fill of a box that is active in the current step. Use the token for
  the hue you mean; never mix a fill by hand.

A static diagram has no motion to show state, so hue does all of that work. Keep one meaning per
hue within a figure, and let `--muted` text and `--line` connectors carry everything that is not
state.

## Effects

`shared/effects.css` is the catalog to copy from, and
[DIAGRAM_STYLE.md](../../.styles/DIAGRAM_STYLE.md#effects) holds the rules that travel with
it. Pick the effect by what it explains:

| Effect | Explains |
|--------|----------|
| Glow | Activation |
| Highlight sweep | Attention passing over a region |
| Comet | Directional movement of data along a path |
| Draw-in | A connection being established |
| Pulse and ripple | An in-place update |
| Shimmer | A pending or loading state |
| Flash | A discrete event |

### Taste

- One lead effect per step. More than about three animated elements at once stops explaining
  and starts competing.
- Every effect explains something. Decoration for its own sake reads as noise on a technical
  blog.
- Design for the blog's column of about 720px. Text that fits at that width but crowds at phone
  width needs fewer words, not a smaller font.

## Accessibility and motion

The rules (labels, keyboard reach, reduced motion, no layout shift) are in the
[hard rules](../../.styles/DIAGRAM_STYLE.md#hard-rules). Two authoring habits make them easy
to meet:

- Write the SVG's `aria-label` as the sentence a reader would need if the figure failed to
  load: what it shows, not what it looks like.
- Write every caption variant before tuning layout. The caption box sizes itself for the
  longest variant, so a long caption added late changes the diagram's height.

## Before you start

Read one or two existing diagrams of the same kind, then follow the
[workflow for a new diagram](../../.styles/DIAGRAM_STYLE.md#workflow-for-a-new-diagram).
The day-to-day commands are in [workflow.md](../development/workflow.md).
