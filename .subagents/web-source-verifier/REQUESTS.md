# Requests — `web-source-verifier`

| # | Question | Status |
|---|---|---|
| R-1 | Should `tools/llama_pin_check.sh` pin the build flags as well as version and commit? | open |
| R-2 | May `AGENTS.md` cite the upstream release page directly instead of only the local check? | answered |

## R-1 — pin scope

**Why it matters.** The check enforces a version and a commit. A different CMake
flag set produces a different binary from the same commit, so "pinned" would be
narrower than a reader assumes.

**Recommendation.** Keep version+commit as the hard pin; document the flag set
as "reviewed, not enforced" until a flag change actually breaks a build.

## R-2 — citing the upstream source (answered 2026-10-29)

**Answer.** Yes. `AGENTS.md` now links
`https://github.com/ggml-org/llama.cpp/releases/tag/v0.5.0` (read on 2026-10-29,
the page states `v0.5.0` and commit `7fe450e`) next to `tools/llama_pin_check.sh:23-24`,
which enforces those two values.
