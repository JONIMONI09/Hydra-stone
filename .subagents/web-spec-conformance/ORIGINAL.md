# ORIGINAL.md — `web-spec-conformance`

> Created **before this sub-agent's first run** (owner directive 2026-10-29).
> Immutable assignment record: never edited after creation; a changed remit
> gets a new `ORIGINAL-<date>.md`.

| Field | Value |
|---|---|
| Sub-agent | `web-spec-conformance` |
| Kind | web research (2 of 3 research, 2 of 6) |
| Created | 2026-10-29 |
| Created by | parent agent (round 12) |
| Repo state | branch `freebuff/6daeacda62104e261f2b28ce`, base `94f8e08` (merge of PR #70) |
| Web access | required — published specifications |

## Original owner assignment (verbatim, German)

> "3 die im Websuchen können"
> "schaue wie Google Agenten SDK die Subs funktionieren etc"

## Normalised assignment (English)

Cross-check what this repository **implements** against what its published
counterparts **specify**: the GGUF specification and the pinned llama.cpp
release, the `.hydra` container definitions in `docs/`, and the Agent Skills
frontmatter convention this repository's skills follow. Every magic number,
enum value, version literal and pinned revision used in code must be traceable
to a documented value on the implementing side and a published definition on
the specification side (R6 in both directions). Report divergences and propose
the correction — never edit.

## Deliverables

| File | Meaning |
|---|---|
| `AGENTS.md` | the contract this sub works under |
| `SKILL.md` | reusable procedure (Agent Skills format, R29/R30) |
| `codegraph.py` | read-only repository graph + the constant/pin cross-check |
| `reports/latest.txt`, `reports/latest.json` | generated evidence of the last run |
| `PROPOSALS.md` | findings and proposals only — this sub never edits code |

## Acceptance criteria

1. Each row pairs an implementation `file:line` with a specification URL or a
   specification `file:line`.
2. An undocumented wire-format constant is a finding (R6), and so is a
   documented capability with no implementation.
3. No statement about a specification without having read it (R26).
4. Nothing outside this folder is modified.
