# PROPOSALS — web-source-verifier

- **Run:** 2026-10-29, `python3 codegraph.py --json reports/latest.json`
- **Evidence:** `reports/latest.txt`, `reports/latest.json`
- **Status:** proposals only — nothing outside this folder was modified.

## Measured

- 31 documents scanned, 17 URLs found.
- 19 documents state a version or a revision pin; **13 of those contain no source
  URL anywhere in the document** (`reports/latest.txt`, "documents that state a
  version/pin ... no source URL anywhere").
- Host census: `codeload.github.com` (3), `dl.google.com` (2),
  `services.gradle.org` (2), `developer.android.com` (2), `man7.org` (2),
  `localhost:8787` (2), and one each for `deb.debian.org`, `arxiv.org`,
  `source.android.com`, `github.com`.

| ID | Claim (`file:line`) | Primary source (URL read) | Verdict | Proposed change | Risk if unchanged |
|---|---|---|---|---|---|
| SV-1 | `AGENTS.md:66-67` — "llama.cpp v0.5.0 ... pinned at 7fe450e..., MIT" | none on the line; the verification exists in-repo at `.agents/docs/ANDROID-AUDIT.md:164-165` (`GET /repos/ggml-org/llama.cpp/releases/latest` returned `tag_name: v0.5.0`) | unverified (pointer missing) | cite the upstream release URL next to the pin in `AGENTS.md` | the pin becomes folklore: a moved or retagged release stays undiscovered |
| SV-2 | `.agents/skills/repo-docs-audit/SKILL.md:27` — "`llama.cpp` is a pinned submodule" | `.gitmodules:1-3` (in-repo, authoritative) | matches | none | n/a |
| SV-3 | 13 documents state pins with no URL at all | `reports/latest.txt` → "documents that state a version/pin" | unverified | for each: add the primary URL, or demote the sentence to "recorded, not verified" | unverified statement reads as verified fact (R26/R6) |

## Method

```bash
python3 .subagents/web-source-verifier/codegraph.py --json reports/latest.json
grep -E "documents that state|no source URL anywhere|host census" reports/latest.txt
```

## Open

- 24 of 31 documents contain no external URL; they are internal records
  (session log, error log, environment notes) that make no external claim. No
  action, recorded so the number is not mistaken for a defect.
- The 13 unsourced pin documents were not all opened individually in this run;
  SV-3 is the queue, not a verified count of wrong pins.

## Status — closed 2026-10-29 (round 13)

SV-1 closed: `AGENTS.md` now cites the primary release page
(<https://github.com/ggml-org/llama.cpp/releases/tag/v0.5.0>, read 2026-10-29 —
the page names `v0.5.0` and shows the release commit `7fe450e`) next to the pin,
and points at `tools/llama_pin_check.sh:23-24` for the enforced values.
SV-3 stays a queue: 13 documents state a pin with no source URL; none was edited
without reading its claim.
