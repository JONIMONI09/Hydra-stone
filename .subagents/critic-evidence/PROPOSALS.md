# PROPOSALS — critic-evidence

- **Run:** 2026-10-29, `python3 codegraph.py --json reports/latest.json`
- **Evidence:** `reports/latest.txt`, `reports/latest.json`
- **Status:** proposals only — nothing outside this folder was modified.

## Measured (live claims only; dated records excluded)

- numeric claims: 29 lines, 13 with a proof pointer on the line, **16 bare**
- capability claims: 125 lines, 53 with a pointer, **72 bare**
- 88 items to triage. The test is a same-line heuristic; a command on the next
  line counts as proof and must be cleared by hand.

| ID | Claim (`file:line`) | Proof present? | What is missing | Severity | Proposed change |
|---|---|---|---|---|---|
| CE-1 | `AGENTS.md:198` "expect \"109 checks, 0 failed\"", `AGENTS.md:202` "contract (34 checks", `AGENTS.md:232` "43 live HTTP tests" | no | these are hard-coded counts in the document that states R21 ("parse the assertion count from the test binary's output; never hard-code an expected number") | major | replace the numbers with the parse instruction and the baseline file pointer; let each gate print its own count |
| CE-2 | `docs/FORMAT.md:348` "7 checks, 0 failures" | yes, on the line above (`docs/FORMAT.md:344` names `tests/test_large_model.c` and `make test-run`) | nothing | cleared | none — heuristic hit, manually cleared |
| CE-3 | 72 bare capability lines across live docs | partly | most are statements whose command sits in the surrounding block (e.g. a rule quoting history) | minor | triage in batches; file only the claims a reader would act on |

## Method

```bash
python3 .subagents/critic-evidence/codegraph.py --json reports/latest.json
grep -E "numeric claims:|capability claims:|total findings" reports/latest.txt
sed -n '340,350p' docs/FORMAT.md      # CE-2 clearance
grep -n "109 checks\|34 checks\|43 live" AGENTS.md   # CE-1 evidence
```

## Open

- CE-3 is deliberately not resolved: 72 lines is more than one pass can clear
  honestly, and marking them "fine" without reading them would be the guessing
  this sub exists to prevent.

## Status — closed 2026-10-29 (round 13)

CE-1 closed: `AGENTS.md` no longer hard-codes counts — `109 checks`, `34 checks`,
`43 live HTTP tests` and `17 pairs` are now "count parsed from output"
(probe: `grep -c '109 checks\|34 checks\|43 live HTTP\|17 pairs' AGENTS.md` → 0).
CE-3 stays partially open: the census still lists 66 bare capability lines.
