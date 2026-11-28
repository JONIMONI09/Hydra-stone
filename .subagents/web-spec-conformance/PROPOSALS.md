# PROPOSALS — web-spec-conformance

- **Run:** 2026-10-29, `python3 codegraph.py --json reports/latest.json`
- **Evidence:** `reports/latest.txt`, `reports/latest.json`
- **Status:** proposals only — nothing outside this folder was modified.

## Measured

- 33 implementation lines carry a 6+ digit hex constant; the audit flags **6
  lines** whose value appears in no `.md`.
- 4 distinct 40-hex revision pins, each mentioned in more than one file.
- Version literals are listed with `file:line` (v1/v3/v4 dispatch in
  `src/hydra_engine.c`, format constants in `include/`).

| ID | Implementation (`file:line`) | Specification (URL or `file:line`) | Divergence | Proposed change | Risk if unchanged |
|---|---|---|---|---|---|
| SC-1 | `include/hydra_v2_container.h:230` and `src/hydra_v2_container.c:93` — CRC-32 known answer `0xCBF43926` | `docs/FORMAT-V2.md` documents the polynomial `0xEDB88320` but not the known-answer value | documented in code only; the format doc cannot be used to validate an implementation | add one line to `docs/FORMAT-V2.md` naming the known-answer pair (`crc32("123456789")`, `crc32("")`) | a third-party implementation cannot self-check its CRC against the spec |
| SC-2 | `tools/server_test.js:358` — `0xdeadbeef` | internal fixture | none: a test vector is not a wire value | none | n/a |
| SC-3 | `android/app/src/main/cpp/llama_jni.cpp:104` — `0x484E4459` (`"HNDY"`) | R22 (fixed seeds) in `.agents/rules.md` | none: internal fixed seed, documented in place | none | n/a |
| SC-4 | `tools/gguf_fixture.js:116` (`0x800000`), `tools/gguf_test.py:855` (`0xFFFFFFFFFFFFFFFF`) | internal bounds/fixtures | none | none | n/a |

## Method

```bash
python3 .subagents/web-spec-conformance/codegraph.py --json reports/latest.json
grep "NOT in any .md" reports/latest.txt
sed -n '225,232p' include/hydra_v2_container.h   # the code's own comment
sed -n '100,106p' android/app/src/main/cpp/llama_jni.cpp
```

## Open

- SC-1 is the only genuine divergence found this run. The GGUF side was not
  re-verified against upstream in this round; the round-9 findings
  (`.agents/errors.md`, quantised-type table) remain the recorded state.

## Status — closed 2026-10-29 (round 13)

SC-1 closed: `docs/FORMAT-V2.md` now states the known-answer pair
(`crc32("123456789") = 0xCBF43926`, `crc32("") = 0x00000000`) beside the `crc32`
field. Re-running this folder no longer lists `0xCBF43926`; the four constants
still flagged are internal test vectors/fixtures (SC-2..SC-4 plus `0x484E4459`,
documented in place) and need no format-doc entry.
