# PROPOSALS — web-tooling-scout

- **Run:** 2026-10-29, `python3 codegraph.py --json reports/latest.json`
- **Evidence:** `reports/latest.txt`, `reports/latest.json`
- **Status:** proposals only — nothing outside this folder was modified.

## Measured

- 21 gate scripts in `tools/`; **19 are referenced by a workflow file**, 2 are not.
- 33 distinct `tools/...` paths are mentioned in live docs; **0 are missing on
  disk** (the 6 hits of the first version were dated records — changelog, error
  log, research log — which are history, not instructions).
- 8 install commands in workflows; toolchain coverage in
  `.agents/Environment.md` recorded for gcc, clang, cppcheck, clang-tidy,
  python3, node, zig, kotlinc and the rest of the probed list.

| ID | Finding | Evidence (`file:line`, command output) | Proposed change | Owner decision needed |
|---|---|---|---|---|
| TS-1 | `tools/kotlin_stub_check/kotlin_stub_check.sh` is run by no workflow | `grep -rn "kotlin_stub_check" .github/workflows/*.yml` → no output; script's own output in this sandbox: `kotlinc not found. Setup: ... npm install kotlin-compiler@2.4.21 ...` | either wire it into `lint.yml` with the documented npm setup, or list it in `AGENTS.md` §3 as a manual-only gate | yes: CI time vs. an unwired gate |
| TS-2 | `tools/fetch_test_model.sh` is run by no workflow | same grep; the script header states the weights are fetched on demand into a directory outside the tree | none: manual by design, documented in its own header | no |
| TS-3 | Local Kotlin type-check cannot run here | `bash tools/kotlin_stub_check/kotlin_stub_check.sh` → `kotlinc not found` (R32: blocked, not measured) | run the recorded npm install before claiming the gate green | no |

## Method

```bash
python3 .subagents/web-tooling-scout/codegraph.py --json reports/latest.json
grep -rn "kotlin_stub_check\|fetch_test_model" .github/workflows/*.yml   # empty
bash tools/kotlin_stub_check/kotlin_stub_check.sh                        # blocked, no kotlinc
```

## Open

- TS-1 is unresolved by design: wiring a Kotlin compiler download into every PR
  is a cost decision for the owner, not for a sub-agent.

## Status — closed 2026-10-29 (round 13)

TS-1 closed by documenting it as a manual-only gate: `AGENTS.md` §3 now lists
`tools/kotlin_stub_check/kotlin_stub_check.sh` with the reason — CI compiles the
real Kotlin sources through Gradle (`ci.yml:739`, `lint.yml:548`), so the stub
check exists for SDK-less sandboxes and costs no CI minutes by design. The
wiring check still prints CHECK for it, which is correct: the fact is documented,
not hidden.
