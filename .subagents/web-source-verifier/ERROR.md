# Error Log — `web-source-verifier`

Append-only, newest entry last. Each entry: what went wrong, the evidence, what
changed because of it.

## 2026-10-29 — the pin filter matched ordinary prose

**What happened.** The first version searched for the word `pin` and produced
~300 hits, almost all of them prose ("pinned", "pinning"). A verifier that
reports prose as a pin is noise.

**Evidence.** `python3 .subagents/web-source-verifier/codegraph.py --top 20` →
300 candidates, none of them a revision string.

**What changed.** The filter now matches only revision shapes: 40-hex commit
ids, `v?<major>.<minor>.<patch>`, `sha256:` digests. Candidate count dropped to
the real pinned values.

## 2026-10-29 — the URL regex captured trailing backticks

**What happened.** URLs inside Markdown table cells were extracted with the
closing backtick and parenthesis, so "has a source" matched a malformed URL.

**Evidence.** First report showed `https://…/v0.5.0`` and `https://…/x)`.

**What changed.** The extractor stops at whitespace, backtick, `)` and `]`.

## 2026-10-29 — line-level counting inflated "documented" checks

**What happened.** 259 line hits looked like a large gap; the real question is
per document, not per line.

**What changed.** The check counts documents with at least one source URL
(13 without, out of 62 `.md`), which is the number a reviewer can act on.
