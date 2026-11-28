---
name: web-spec-conformance
description: "Cross-check implemented format constants, magic numbers, pinned revisions and version literals against the published specification and the in-tree docs, and report every divergence with both sides cited."
---

# Web Spec Conformance

## When to use

Use when implemented constants, magic numbers or pinned revisions must be compared against the published specification. Not for prose claims about capability.

Use when a wire-format constant, enum value, version literal or pinned revision
is touched, documented, or about to be claimed as conformant.

## Why this exists

This repository implements its own container (`docs/FORMAT.md`,
`docs/FORMAT-V2.md`) and consumes another one (GGUF through a pinned
llama.cpp). A constant that drifts from its specification produces files that
load nowhere; a constant nobody documented produces a capability claim with no
backing (R6 in both directions). Round 9 found exactly this class of bug: a
quantised-type name table that disagreed with the official enum, so a user
would have been told the wrong layout name.

## Procedure

1. **Inventory.** `python3 codegraph.py --json reports/latest.json` lists hex
   constants with `file:line`, 40-hex revision pins with every file that
   carries them, and version literals.
2. **Documented?** Each constant is marked `documented` or `NOT in any .md`.
   Classify every `NOT`: wire value (must be documented) or internal detail
   (must stay out of the format docs).
3. **One value?** A pin or magic number appearing with two different values in
   two files is a defect — report both `file:line`s and do not pick a winner.
4. **Read the source.** Open the specification section that governs the value
   and quote it. Where the in-tree docs and the code disagree, the code is the
   implementation and the doc is the claim: report the claim.
5. **Report** in `PROPOSALS.md`, then re-run the script so the report matches
   the tree you judged.

## Evidence rules

- Both sides cited: implementation `file:line`, specification URL or in-tree
  `file:line`.
- A "looks consistent" verdict without the read page is not a verdict.
- Do not propose a dependency bump; propose the check that would catch drift.

## Anti-patterns

- Declaring conformance from the repository's own docs alone.
- Silent numeric normalisation ("0x41 == 65, so fine") without naming the unit
  and endianness the specification defines.
- Editing anything at all: this sub-agent proposes only.
