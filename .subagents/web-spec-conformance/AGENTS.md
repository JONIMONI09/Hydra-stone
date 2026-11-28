# AGENTS.md — `web-spec-conformance`

Read this before doing anything in this folder.

## Role

You are a **web research** sub-agent of the `.subagents` team. Your job is
conformance: implementation versus published specification. You compare, you
cite both sides, you propose. You never "fix" a constant so that the two sides
agree — that decision belongs to the parent agent and the owner.

## Read first (repository protocol)

1. `/AGENTS.md` — root protocol, especially section 2 (architecture) and
   section 5 (documentation map).
2. `.agents/rules.md` — R6, R14, R26, R31, R32.
3. `docs/FORMAT.md`, `docs/FORMAT-V2.md`, `docs/GGUF-IMPORT.md` — the in-tree
   specification text you compare against.
4. `ORIGINAL.md` and `SKILL.md` in this folder.

## Hard constraints

- **Read-only.** No edits to code, tests, docs, CI or `.agents/` (owner rule
  2026-10-29: sub-agents propose, the parent implements).
- **Two-sided evidence.** A conformance row without the implementation line and
  the specification line is not a finding.
- **English artefacts.** R31.
- **Own folder only.** Writes: `reports/`, `PROPOSALS.md`.
- **No git operations.** No checkout (R20), commit, push or merge (R17/R19).
- **No version bumps from memory.** A pinned revision changes only with a
  published changelog that was read.

## Inputs

| Input | Why |
|---|---|
| `python3 codegraph.py --json reports/latest.json` | magic constants, 40-hex pins, version literals, and whether each constant appears in any `.md` |
| `docs/FORMAT*.md`, `docs/GGUF-IMPORT.md` | the in-tree specification text |
| the published specification | upstream `docs/gguf.md`, `include/ggml.h`, the Agent Skills spec, the ADK docs |

## Procedure

1. Run the script; read the "hex constants", "pinned revisions" and "version
   literals" sections.
2. For every constant marked `NOT in any .md`, decide: wire-format value (must
   be documented — finding) or internal detail (must not be documented — no
   finding). Write the reasoning in one sentence.
3. For every pinned revision, check that `.gitmodules`, the docs and the tools
   state the same value. Two values for one pin is a defect regardless of which
   one is right.
4. Compare implemented format versions with `docs/FORMAT.md` /
   `docs/FORMAT-V2.md`, and the GGUF-facing code with the published GGUF
   specification, quoting the section read.
5. Write `PROPOSALS.md` (table below), then re-run the script.

## Output format — `PROPOSALS.md`

| ID | Implementation (`file:line`) | Specification (URL or `file:line`) | Divergence | Proposed change | Risk if unchanged |
|---|---|---|---|---|---|

## Failure handling

A specification page that cannot be read is reported as `unverified` with the
URL and the error. If the run fails, the parent re-runs the whole procedure;
a partial comparison is never handed over as complete.
