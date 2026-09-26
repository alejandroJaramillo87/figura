# Diagrams

Every diagram in the library, one directory per consumer location: a blog post's filename stem,
a series directory, or a docs-site section.

The catalog below is rendered from `manifest.json` by `npm run docs`. Each entry's `consumers`
names the pages that embed or copy it, as `<repo>:<path>`; read it before renaming or removing
a diagram.

<!-- inventory:catalog:start -->

### ai-experiments

| Diagram | Kind | Shows | Used by |
|---------|------|-------|---------|
| [tier-loop](ai-experiments/tier-loop.html) | static | The three repository tiers and the artifacts that cross between them, each with a contract file under schemas/. | `ai-experiments:site/static/img/diagrams/tier-loop.svg`<br>`ai-experiments:site/docs/index.md` |

### ai-rig-hardware

| Diagram | Kind | Shows | Used by |
|---------|------|-------|---------|
| [component-overview](ai-rig-hardware/component-overview.html) | hover-inspect | CPU, GPU, RAM and the two NVMe drives laid out on the board, each labelled with the workload limit it sets. | `curiosity-chronicles:content/posts/ai-rig-hardware.md` |
| [pcie-lane-budget](ai-rig-hardware/pcie-lane-budget.html) | hover-inspect | Where the CPU's PCIe lanes go: x16 to the RTX 5090, x4 CPU-direct to the data drive, x4 to the chipset, and two M.2 slots left empty on purpose. | `curiosity-chronicles:content/posts/ai-rig-hardware.md` |
| [power-thermal](ai-rig-hardware/power-thermal.html) | step-timeline | A five-step build-up from the idle floor to roughly 800W with both compute paths loaded, against a 1200W supply, ending with the case airflow that carries the heat out. | `curiosity-chronicles:content/posts/ai-rig-hardware.md` |

### effects-sampler

| Diagram | Kind | Shows | Used by |
|---------|------|-------|---------|
| [effects-sampler](effects-sampler/effects-sampler.html) | hover-inspect | Living documentation: all seven catalog effects (glow, sweep, comet, draw-in, ripple, shimmer, flash) running in the classic palette, with accent and dim-fill swatches. | none |

### inference-containers

| Diagram | Kind | Shows | Used by |
|---------|------|-------|---------|
| [engine-comparison](inference-containers/engine-comparison.html) | hover-inspect | Grid comparing llama-cpu, llama-gpu, and vllm-gpu: hardware, optimization target, image build style, and entrypoint pattern. | `curiosity-chronicles:content/posts/inference-containers-overview.md` |
| [llama-cpu-build-pipeline](inference-containers/llama-cpu-build-pipeline.html) | step-timeline | Shared trixie-slim base, Zen 5 toolchain, SHA-pinned llama.cpp, AVX-512 cmake configuration, and the minimal runtime stage. | `curiosity-chronicles:content/posts/inference-containers-llama-cpu.md` |
| [llama-cpu-entrypoint-flow](inference-containers/llama-cpu-entrypoint-flow.html) | hover-inspect | Required, defaulted, feature-flag, and advanced env var groups feeding the CMD_ARGS bash array, ending in exec. | `curiosity-chronicles:content/posts/inference-containers-llama-cpu.md` |
| [llama-gpu-entrypoint-flow](inference-containers/llama-gpu-entrypoint-flow.html) | hover-inspect | Base config, GPU offload knobs, feature flags, and the NSYS_PROFILE wrapper assembling the GPU server command. | `curiosity-chronicles:content/posts/inference-containers-llama-gpu.md` |
| [llama-gpu-stage-split](inference-containers/llama-gpu-stage-split.html) | hover-inspect | CUDA devel builder with sm_120 flags and the stub libcuda, the runtime stage receiving only the binary, and the host driver arriving at run time. | `curiosity-chronicles:content/posts/inference-containers-llama-gpu.md` |
| [vllm-build-vs-wheel](inference-containers/vllm-build-vs-wheel.html) | hover-inspect | The retired from-source sm_120 build versus the current single-stage cu130 wheel install with pinned uv and FlashInfer. | `curiosity-chronicles:content/posts/inference-containers-vllm.md` |
| [vllm-entrypoint-flow](inference-containers/vllm-entrypoint-flow.html) | hover-inspect | MODEL_PATH as the single required variable, VRAM and batching defaults, precision selectors, and the assembled vllm serve command. | `curiosity-chronicles:content/posts/inference-containers-vllm.md` |

### inference-loop

| Diagram | Kind | Shows | Used by |
|---------|------|-------|---------|
| [kv-cache-fill](inference-loop/kv-cache-fill.html) | step-timeline | Prefill writes K/V for the whole prompt in one pass; each decode step appends one row and attends over everything cached. | `curiosity-chronicles:content/posts/diagram-test.md`<br>`curiosity-chronicles:content/posts/hello-world.md` |

### linux-ai-setup

| Diagram | Kind | Shows | Used by |
|---------|------|-------|---------|
| [gpu-software-stack](linux-ai-setup/gpu-software-stack.html) | hover-inspect | Five layers from frameworks and containers down to the RTX 5090 silicon: cuDNN, CUDA toolkit, driver and kernel modules. | `curiosity-chronicles:content/posts/linux-ai-setup.md` |
| [setup-pipeline](linux-ai-setup/setup-pipeline.html) | step-timeline | Eight-stage setup order as a vertical pipeline from Ubuntu install to Docker with the NVIDIA Container Toolkit: each stage lights up with its script, a comet carries the flow downward, and reboot points flash. | `curiosity-chronicles:content/posts/linux-ai-setup.md` |
| [storage-layout](linux-ai-setup/storage-layout.html) | hover-inspect | 1TB OS drive vs 2TB data drive mounted at /mnt/ai-data: models, datasets, caches, workspace, and an ambient comet riding the cache symlinks that keep home lean. | `curiosity-chronicles:content/posts/linux-ai-setup.md` |

### llm-training

| Diagram | Kind | Shows | Used by |
|---------|------|-------|---------|
| [training-loop](llm-training/training-loop.html) | step-timeline | One optimization step: forward comets through the layer chain, loss glow, backward gradient comets, weight-update ripples. | `curiosity-chronicles:content/posts/diagram-test.md` |

### prefill-vs-decode

| Diagram | Kind | Shows | Used by |
|---------|------|-------|---------|
| [attention-pattern](prefill-vs-decode/attention-pattern.html) | step-timeline | Causal attention matrix: prefill fills prompt rows in one batched pass, decode adds one row per step. | `curiosity-chronicles:content/posts/diagram-test.md` |

### rust-harness

| Diagram | Kind | Shows | Used by |
|---------|------|-------|---------|
| [interp-loop](rust-harness/interp-loop.html) | static | The capture, train, export, load, serve, and monitor loop between the rust harness and the interp tier. | `ai-experiments:site/static/img/diagrams/interp-loop.svg`<br>`ai-experiments:site/docs/interp/index.md` |
| [interp-observability-grains](rust-harness/interp-observability-grains.html) | static | The four interp observability mechanisms ordered by grain, with how each is enabled and the run id that joins them. | `ai-experiments:site/static/img/diagrams/interp-observability-grains.svg`<br>`ai-experiments:site/docs/interp/observability/index.md` |
| [observability-grains](rust-harness/observability-grains.html) | static | The five harness observability mechanisms ordered by grain, from one run to one instruction, with how each is enabled and the run id that joins the in-process three. | `ai-experiments:site/static/img/diagrams/observability-grains.svg`<br>`ai-experiments:site/docs/rust-harness/observability/index.md` |

### sandboxing

| Diagram | Kind | Shows | Used by |
|---------|------|-------|---------|
| [agent-egress-flow](sandboxing/agent-egress-flow.html) | step-timeline | The agent on an internal network with no internet route, the Squid proxy as the only door, and the allow/deny verdict per request. | `curiosity-chronicles:content/posts/sandboxing-agents.md` |
| [comparison-grid](sandboxing/comparison-grid.html) | hover-inspect | Comparison grid of the inference, training, Mech Interp, and agent sandboxes: what each workload must write, where it must talk, GPU access, and lifecycle — over a shared hardening floor. | none |
| [inference-topology](sandboxing/inference-topology.html) | hover-inspect | Localhost-only port bindings crossing into the ai-network bridge, three hardened inference containers, and the read-only model mount. | `curiosity-chronicles:content/posts/sandboxing-inference.md` |
| [interp-workbench](sandboxing/interp-workbench.html) | hover-inspect | Hover-inspect map of the Mech Interp sandbox: JupyterLab on 127.0.0.1:8888 with a per-launch token, the shared hardening floor on an isolated bridge, one reserved GPU behind a preflight check, and four mounts including the read-write repo at /workspace. | none |
| [training-job-lifecycle](sandboxing/training-job-lifecycle.html) | step-timeline | One training job end to end: compose run --rm creates the hardened container, mounts attach, the job runs on the reserved GPU, checkpoints land on the writable training root, the container is removed. | none |

### transformer-architecture

| Diagram | Kind | Shows | Used by |
|---------|------|-------|---------|
| [block-dataflow](transformer-architecture/block-dataflow.html) | hover-inspect | Pre-norm block: RMSNorm → attention → residual add → RMSNorm → SwiGLU MLP → residual add. | `curiosity-chronicles:content/posts/diagram-test.md` |

### what-language-leaves-out

| Diagram | Kind | Shows | Used by |
|---------|------|-------|---------|
| [agreement-distance](what-language-leaves-out/agreement-distance.html) | toggle | Toggle an intervening singular distractor into “The keys (to the cabinet) are on the table” — the agreement arc stretches over the flagged attractor. | `curiosity-chronicles:content/posts/what-language-leaves-out-syntactic.md` |
| [ambiguity-ladder](what-language-leaves-out/ambiguity-ladder.html) | hover-inspect | Hover the linguistic hierarchy from lexical to pragmatic, plus the LLM-specific structural dependencies that run alongside every level. | `curiosity-chronicles:content/posts/what-language-leaves-out-intro.md` |
| [bridging-implicit](what-language-leaves-out/bridging-implicit.html) | toggle | “I entered the room. | `curiosity-chronicles:content/posts/what-language-leaves-out-referential.md` |
| [cataphora-order](what-language-leaves-out/cataphora-order.html) | step-timeline | Step timeline of a causal model reading “Before she left, Mary locked the door.” — the mask slides right, “she” stays unresolved until “Mary” arrives and the arc draws backward. | `curiosity-chronicles:content/posts/what-language-leaves-out-referential.md` |
| [code-binding](what-language-leaves-out/code-binding.html) | toggle | A variable use re-binds from a module-level definition to an inserted shadowing one -- coreference over code tokens. | `curiosity-chronicles:content/posts/what-language-leaves-out-structural.md` |
| [comparative-ellipsis](what-language-leaves-out/comparative-ellipsis.html) | toggle | Toggle between the two reconstructions of “I like her more than John” — than John [likes her] vs than [I like] John — with different ghost completions. | `curiosity-chronicles:content/posts/what-language-leaves-out-semantic.md` |
| [coordination-scope](what-language-leaves-out/coordination-scope.html) | toggle | Toggle the grouping of “old men and women” — the adjective's scope bracket re-draws and membership cards show who inherits it. | `curiosity-chronicles:content/posts/what-language-leaves-out-syntactic.md` |
| [coref-chain](what-language-leaves-out/coref-chain.html) | step-timeline | Step timeline threading “Dr. | `curiosity-chronicles:content/posts/what-language-leaves-out-referential.md` |
| [definite-pick](what-language-leaves-out/definite-pick.html) | toggle | “The animal” must pick between a mentioned dog and cat; toggling the sentence's ending re-points the description via world knowledge. | `curiosity-chronicles:content/posts/what-language-leaves-out-referential.md` |
| [deixis-chat](what-language-leaves-out/deixis-chat.html) | toggle | A three-turn transcript where "I" and "you" re-bind to opposite speakers on every turn; arcs to the speaker labels. | `curiosity-chronicles:content/posts/what-language-leaves-out-pragmatic.md` |
| [delimiter-match](what-language-leaves-out/delimiter-match.html) | toggle | Deleting one distant opening quote flips every later quote's role between OPEN and CLOSE and re-shades string vs code. | `curiosity-chronicles:content/posts/what-language-leaves-out-structural.md` |
| [demonstrative-scope](what-language-leaves-out/demonstrative-scope.html) | toggle | “That was a mistake.” — a bracket over the previous sentence grows from one act to the whole decision; the referent's size is the ambiguity. | `curiosity-chronicles:content/posts/what-language-leaves-out-referential.md` |
| [discourse-relation](what-language-leaves-out/discourse-relation.html) | toggle | "He fell. | `curiosity-chronicles:content/posts/what-language-leaves-out-pragmatic.md` |
| [domain-tint](what-language-leaves-out/domain-tint.html) | toggle | The same sentence inside an oncology note and a product review; diffuse arcs show the register of the whole document pinning the sense. | `curiosity-chronicles:content/posts/what-language-leaves-out-lexical.md` |
| [entity-flip](what-language-leaves-out/entity-flip.html) | toggle | Sentence-initial "Turkey was dry." with a context toggle flipping entity-hood — capitalization is forced at sentence start, so it carries no signal. | `curiosity-chronicles:content/posts/what-language-leaves-out-lexical.md` |
| [filler-gap](what-language-leaves-out/filler-gap.html) | toggle | “Which book did you say Mary thought John read __?” — the fronted phrase carries a pending badge until the gap site is revealed two clauses downstream. | `curiosity-chronicles:content/posts/what-language-leaves-out-syntactic.md` |
| [format-continuation](what-language-leaves-out/format-continuation.html) | toggle | The same content under a markdown-table vs numbered-list precedent; the ghost continuation's shape follows the pattern, not the grammar. | `curiosity-chronicles:content/posts/what-language-leaves-out-structural.md` |
| [gapping-ellipsis](what-language-leaves-out/gapping-ellipsis.html) | toggle | Reveal toggle materializing the elided material in VP-ellipsis (“Mary can __ too”) and sluicing (“I don't know who __”) with copy-in arcs. | `curiosity-chronicles:content/posts/what-language-leaves-out-syntactic.md` |
| [garden-path](what-language-leaves-out/garden-path.html) | step-timeline | Step timeline of the incremental parse of “The horse raced past the barn fell” — commitment, contradiction at “fell”, and visible reanalysis to the reduced relative. | `curiosity-chronicles:content/posts/what-language-leaves-out-syntactic.md` |
| [gradable-scale](what-language-leaves-out/gradable-scale.html) | toggle | Noun-swap toggle re-anchors the scale bar under “tall” from toddler (~1 m) to building (~150 m) while the adjective token stays fixed. | `curiosity-chronicles:content/posts/what-language-leaves-out-semantic.md` |
| [heads-tendency](what-language-leaves-out/heads-tendency.html) | hover-inspect | Four named head tendencies (induction the only found circuit) beside a dashed majority of unnamed heads. | `curiosity-chronicles:content/posts/what-language-leaves-out-capstone.md` |
| [homograph-voicing](what-language-leaves-out/homograph-voicing.html) | toggle | Toggle "lead" between /lɛd/ metal and /liːd/ news-lead contexts; the listener lane hears the sense, the model lane sees four letters. | `curiosity-chronicles:content/posts/what-language-leaves-out-lexical.md` |
| [idiom-binding](what-language-leaves-out/idiom-binding.html) | toggle | Toggle "kicked the bucket" between the compositional decoy and the idiomatic reading, where three tokens fuse into one unit meaning died. | `curiosity-chronicles:content/posts/what-language-leaves-out-lexical.md` |
| [implicature-gap](what-language-leaves-out/implicature-gap.html) | toggle | "Did you like the movie?" / "The popcorn was good." — toggle materializes the implicated verdict carried by the unaddressed question. | `curiosity-chronicles:content/posts/what-language-leaves-out-pragmatic.md` |
| [induction-copy](what-language-leaves-out/induction-copy.html) | step-timeline | Step timeline of the induction-head loop: match the current token to its previous occurrence, hop one forward, copy the successor. | `curiosity-chronicles:content/posts/what-language-leaves-out-structural.md` |
| [instruction-binding](what-language-leaves-out/instruction-binding.html) | toggle | Swapping a distant instruction header flips the same passage's role and continuation -- the series' longest-range dependency. | `curiosity-chronicles:content/posts/what-language-leaves-out-structural.md` |
| [ladder-depth](what-language-leaves-out/ladder-depth.html) | hover-inspect | The series' six levels beside a model-depth column, connected by deliberately soft bands -- tendencies, not an org chart. | `curiosity-chronicles:content/posts/what-language-leaves-out-capstone.md` |
| [metaphor-suppress](what-language-leaves-out/metaphor-suppress.html) | toggle | Object-swap toggle: “drowning in the pool” vs “drowning in paperwork” — the literal water-sense is struck through and the figurative mapping lights. | `curiosity-chronicles:content/posts/what-language-leaves-out-semantic.md` |
| [metonymy-standin](what-language-leaves-out/metonymy-standin.html) | toggle | Dereference toggle: “The White House announced…” hands off from the literal building to a dashed ghost node for the people inside; Shakespeare and ham-sandwich companions. | `curiosity-chronicles:content/posts/what-language-leaves-out-semantic.md` |
| [modal-flavor](what-language-leaves-out/modal-flavor.html) | toggle | Context-swap toggle flips “You must be tired” between epistemic inference and deontic obligation; the flavor is imported from one context line. | `curiosity-chronicles:content/posts/what-language-leaves-out-semantic.md` |
| [modifier-scope](what-language-leaves-out/modifier-scope.html) | toggle | Toggle slides the scope bracket of “only” in “I only ate the cake” between the verb and the object; glosses cross-fade. | `curiosity-chronicles:content/posts/what-language-leaves-out-syntactic.md` |
| [negation-scope](what-language-leaves-out/negation-scope.html) | toggle | Toggle slides the NOT bracket in “I didn't leave because I was angry” between narrow and wide scope; outcome cards (I stayed / I left) light per reading. | `curiosity-chronicles:content/posts/what-language-leaves-out-semantic.md` |
| [one-anaphora](what-language-leaves-out/one-anaphora.html) | toggle | Toggle reveals the elided noun as a ghost token after “one”, with a copy-in arc from “shirt” in the previous utterance. | `curiosity-chronicles:content/posts/what-language-leaves-out-referential.md` |
| [polysemy-web](what-language-leaves-out/polysemy-web.html) | hover-inspect | Hover the sense hub: material, newspaper, article, exam radiating from a shared conceptual core — relatives, not homonymy's colliding strangers. | `curiosity-chronicles:content/posts/what-language-leaves-out-lexical.md` |
| [pos-flip](what-language-leaves-out/pos-flip.html) | toggle | Switch between the two grammars of the same five tokens: flies as noun or verb, like as verb or preposition, brackets re-drawing per reading. | `curiosity-chronicles:content/posts/what-language-leaves-out-lexical.md` |
| [pp-attachment](what-language-leaves-out/pp-attachment.html) | toggle | Toggle between verb and noun attachment for “I saw the man with the telescope” — brackets and information-need arc re-draw between the two structures. | `curiosity-chronicles:content/posts/what-language-leaves-out-syntactic.md` |
| [presupposition-split](what-language-leaves-out/presupposition-split.html) | toggle | "John stopped smoking" split into asserted and presupposed cards; negation flips only the asserted card. | `curiosity-chronicles:content/posts/what-language-leaves-out-pragmatic.md` |
| [quantifier-scope](what-language-leaves-out/quantifier-scope.html) | toggle | Toggle over “Every student read a book” re-draws the student→book mapping between one shared book and one book each; loop-order glosses. | `curiosity-chronicles:content/posts/what-language-leaves-out-semantic.md` |
| [register-frame](what-language-leaves-out/register-frame.html) | toggle | The same sentence inside a statute and a physics paper; the document's register re-glosses "state" and "notice" wholesale. | `curiosity-chronicles:content/posts/what-language-leaves-out-pragmatic.md` |
| [role-assignment](what-language-leaves-out/role-assignment.html) | toggle | Active ⇄ passive toggle for “The dog bit the man” — AGENT and PATIENT tags stay with the participants while surface order flips. | `curiosity-chronicles:content/posts/what-language-leaves-out-syntactic.md` |
| [sarcasm-flip](what-language-leaves-out/sarcasm-flip.html) | toggle | "Great, another meeting." — swapping the preceding discourse line flips the sentiment tag on "Great" without changing a token. | `curiosity-chronicles:content/posts/what-language-leaves-out-pragmatic.md` |
| [sense-pinning](what-language-leaves-out/sense-pinning.html) | toggle | Toggle the preceding sentence and watch one distant word pin the sense of "bank", with an information-need arc to the disambiguating cue. | `curiosity-chronicles:content/posts/what-language-leaves-out-lexical.md` |
| [soft-lookup](what-language-leaves-out/soft-lookup.html) | step-timeline | Step timeline re-answering the Winograd pronoun with the mechanism: query, graded matches, weighted blend -- a mixture, never a pointer. | `curiosity-chronicles:content/posts/what-language-leaves-out-capstone.md` |
| [speech-act](what-language-leaves-out/speech-act.html) | toggle | "Can you pass the salt?" dispatched to a question handler vs a request handler; the literal answer is technically responsive, socially broken. | `curiosity-chronicles:content/posts/what-language-leaves-out-pragmatic.md` |
| [subword-fusion](what-language-leaves-out/subword-fusion.html) | step-timeline | Step timeline: unbelievable splits into three meaningless fragments, binds to its neighbors, and re-assembles as one concept across three positions. | `curiosity-chronicles:content/posts/what-language-leaves-out-lexical.md` |
| [tense-aspect](what-language-leaves-out/tense-aspect.html) | toggle | Toggle flips “I've lived here” / “I lived here” on a timeline bar; a Mandarin row shows a dashed empty tense slot filled by a context adverb. | `curiosity-chronicles:content/posts/what-language-leaves-out-semantic.md` |
| [topic-tracking](what-language-leaves-out/topic-tracking.html) | toggle | Changing which entity the opening sentence establishes as topic re-points a later "it" between bridge and river. | `curiosity-chronicles:content/posts/what-language-leaves-out-pragmatic.md` |
| [winograd-toggle](what-language-leaves-out/winograd-toggle.html) | toggle | Switch a single verb and watch the pronoun's information-need arc move between two antecedents. | `curiosity-chronicles:content/posts/what-language-leaves-out-intro.md`<br>`curiosity-chronicles:content/posts/what-language-leaves-out-referential.md` |
| [zero-anaphora](what-language-leaves-out/zero-anaphora.html) | toggle | Spanish pro-drop: “¿Y María? — Llegó tarde.” — a dashed empty-slot token carries the arc back to María; the referent has no surface token at all. | `curiosity-chronicles:content/posts/what-language-leaves-out-referential.md` |

<!-- inventory:catalog:end -->
