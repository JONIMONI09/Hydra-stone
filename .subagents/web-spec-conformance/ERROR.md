# Error Log — `web-spec-conformance`

Append-only, newest last.

## 2026-10-29 — the detector counted its own proposals as documentation

**What happened.** After one round of reporting, every undocumented constant
suddenly looked documented: the "documented" corpus was *all* Markdown, which
included `.subagents/*/PROPOSALS.md` — the file that names the constant in order
to report it.

**Evidence.** `0xCBF43926` disappeared from the undocumented list without any
docs change; the run reported 0 candidates while `docs/FORMAT-V2.md` had not
mentioned CRC yet.

**What happened next.** `.subagents/` was excluded from the corpus, and the
constant was documented for real in `docs/FORMAT-V2.md`.

## 2026-10-29 — 40-hex commit ids were counted as format constants

**What happened.** The 40-hex rule is for pinned revisions *and* for hashes in
prose; both were reported as "undocumented constant".

**What changed.** 40-hex values are now reported only when a format word
(`crc`, `magic`, `checksum`) appears on the same line; otherwise they are
pins and belong to `web-source-verifier`.
