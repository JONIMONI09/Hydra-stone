---
name: web-source-verifier
description: "Verify the repository's external claims (versions, API behaviour, format constants, tool flags) against primary sources and report each as matches, mismatch or unverified with the URL read."
---

# Web Source Verifier

## When to use

Use when a document states an external fact: a version, a flag, an API behaviour, a format constant. Not for internal consistency between two of our own files - that is `web-spec-conformance`.

Use when a document, skill or code comment makes a statement about something
outside this repository and that statement is about to be relied on: a pinned
version, a library behaviour, a format specification, a CLI flag, a CVE id.

## Why this exists

`.agents/rules.md` R26: "CVE IDs, tool names and API behaviour are verified on
the web and in a local run, never taken from a description." A wrong
attribution is itself a documentation bug, and a version pin nobody checked is
a supply-chain claim without evidence.

## Inputs

- `python3 codegraph.py --json reports/latest.json` — the repo graph plus the
  URL/pin census: it lists every `file:line` that pins a version without a URL
  on the same line.
- The primary source itself: upstream repo, vendor docs, standards body.

## Procedure

1. **Build the queue.** Run the script; take the pin/version claims that have
   no URL on the line.
2. **Classify the host.** `github.com/ggml-org`, `adk.dev`,
   `developer.android.com`, `kernel.org`, `w3.org`, `nvd.nist.gov` count as
   primary. A blog, a forum answer or an LLM answer does not, however right it
   looks.
3. **Read, do not skim.** Record the exact URL and the sentence that settles
   the claim. If the page moved, say so rather than guessing the new one.
4. **Verdicts.** `matches` (repo agrees with the source), `mismatch` (repo is
   wrong: write the proposed correction), `unverified` (no primary source
   found; the claim must not be presented as fact).
5. **Report** in `PROPOSALS.md` with the table from `AGENTS.md`, then re-run
   the script so `reports/latest.*` matches the judged tree.

## Evidence rules

- One row per claim; no row without `file:line` and, for `matches`/`mismatch`,
  a URL.
- Quote the source sentence verbatim; paraphrase only in the proposal column.
- Numbers about this repository (test counts, timings) are not this remit —
  `critic-evidence` owns them.

## Anti-patterns

- Citing the repository itself as the source of its own claim.
- "According to the docs" with no URL.
- Marking `matches` because the claim sounds plausible.
- Widening the remit into implementation: this sub proposes, the parent edits.
