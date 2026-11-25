# Hydra-Stone — what this is

A small, self-contained **AI inference tool in C**. It loads a `.hydra`
model file and generates tokens from a starting point. The command-line
runner, the web console and the Android app all drive the **same engine**,
so the same inputs give the same outputs on every surface — no server,
no network, no runtime install step.

## Try it

```sh
python3 tools/make_model.py model.hydra      # build a starter model
./hydra-run model.hydra 123                  # start at token 123, greedy, 16 steps
./hydra-run model.hydra 123 8 \
     --prompt 7,9,11 \
     --temp 0.8 --min-p 0.1 \
     --rep-penalty 1.2 --rep-window 32 \
     --seed 42 --json
```

## How it works, in one breath

- **The model file is memory-mapped, not copied.** The engine `mmap`s
  the `.hydra` file and reads weights straight from the mapped pages:
  no heap allocation for weights, no load-into-RAM step, and the
  working set per step is a small fixed scratch buffer. Load time is
  a page fault, not a file copy.
- **Each step** pushes one token through the fixed-size state machine,
  scores the vocabulary, and picks the next token.
- **Sampling is opt-in and deterministic by default.** Temperature `0`
  (the default) is pure greedy — bit-identical, no randomness. Setting
  `--temp > 0` activates the stochastic path, where:
  - **temperature** reshapes the distribution (low = sharp, high = flat),
  - the **repetition penalty** (over a **window** of recent tokens)
    discourages reusing what was just said,
  - the **min-p filter** — this project's nucleus-style filter — drops
    every token with `P(c) < min-p · p_max`, trimming the unreliable
    tail while keeping the mass where the model is confident,
  - **`--seed` pins the RNG stream**: same seed + same parameters =
    the same tokens, verifiable on the CLI, the web API and the
    Android bridge alike.
- **One engine, three surfaces.** `hydra-run` is the CLI; the web
  console (`server.js`, `/api/infer`) spawns that same binary per
  request; the Android app links the same C engine through JNI. A CI
  gate (`tools/sampler_contract_check.sh`) pins the sampler ranges
  across all three surfaces so one request cannot behave differently
  depending on where it was typed.

## What it does today (verified 2026-10-25)

- Loads **v1 `.hydra`** (ternary-aggregate models) and **v2
  `.hydra2`** (sparse MoE: F32 / ternary / Q4_0 experts, optional
  embedded BPE vocabulary) — one binary, `--inspect` tells you which
  file you have.
- **CLI:** start token, step count, `--prompt` (token-ID list),
  `--text-prompt` (BPE text on `.hydra2`), every sampler flag above,
  plain text **or** `--json` output, `--bench`, `--fast`.
- **Web console:** REST API over the same binary — model upload,
  GGUF import, in-browser training, and inference with the full
  sampler configuration **including the seed**; browser UI included.
- **Android:** the same engine over JNI, models bundled in the APK.
- **Verification:** seven C test suites plus the Node server suite
  (61 tests) run in CI on every push, with ASan/UBSan and the
  cross-surface sampler contract gate.

## Watch this to understand the ideas

| Video (all public) | What it explains |
| --- | --- |
| [3Blue1Brown — *Large Language Models explained briefly* (2024, 8 min)](https://www.youtube.com/watch?v=LPZh9BOjkQs) | The one core idea: models predict the next token. Everything else builds on it. |
| [*Gentle Introduction to LLM Sampling: Greedy, Top-k, Top-p, and Temperature* (2026)](https://www.youtube.com/watch?v=M4X07FFRKik) | The decoding menu this sampler works from. |
| [*The Secret Controls for your LLM: Temperature, Top-K, Top-P, etc.* (2026)](https://www.youtube.com/watch?v=MkaazQttbpc) | Exactly the flags `hydra-run` has: temperature, top-k, top-p, **min-p**, repeat penalty. |
| [Andrej Karpathy — *Deep Dive into LLMs like ChatGPT* (2025, 3.5 h)](https://www.youtube.com/watch?v=7xTGNNLPyMI) | The whole picture for general audiences. |

> **Note on "nucleus":** most toolkits ship the classical top-p (nucleus)
> filter; this project ships **min-p** instead — same goal (cut the
> unreliable tail), different rule. Min-p keeps every token with
> `P(c) ≥ min-p · p_max`, so the cut adapts to the *peak* of the
> distribution rather than a fixed cumulative mass. The 2026 sampling
> videos above cover both, and the min-p semantics are documented in
> `include/hydra_model.h` (sampler contract section).
