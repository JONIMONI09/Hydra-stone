# Final review — 2026-10-29, round 12 (`.subagents` team)

**Score: 9/10** — PASS (threshold is 7/10). One point withheld under
criterion 4; the reason is written below so it is not a matter of taste.

Reviewed artefacts: the whole `.subagents/` tree, the new parent skill
`.agents/skills/sub-agents/SKILL.md`, and this round's records
(`.agents/session.md` round 12, `.agents/errors.md` 2026-10-29 entries,
`.agents/user.md` directives 31-32, `.agents/README.md`, `CHANGELOG.md`).

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | Structure (2) | **2/2** | `check_subagents.py`: 20 checks, 0 failures; preflight `folders ready: 6/6`, every folder with `ORIGINAL.md`, `AGENTS.md`, `SKILL.md`, `codegraph.py`, `PROPOSALS.md` (1.1-2.3 kB each) and `reports/latest.json` |
| 2 | Skills (1) | **1/1** | six member skills plus `sub-agents` pass the ASCII / quoted-description / `name == directory` rules; gate output line per folder |
| 3 | Code graph (2) | **2/2** | `run_all.py` 6/6 `rc=0`, first attempt each; every report describes 226 files, 61 `.md`, 30 open checkboxes, 4 source markers — counts match `codegraph_core.py` run standalone |
| 4 | Evidence (2) | **1/2** | every proposal row carries a `file:line` or a command output (spot-checked: `AGENTS.md:198/202/232`, `tools/gguf_reader.py:576`, `tools/safetensors_to_hydra.py:229`, `include/hydra_v2_container.h:230`, empty `grep` for `kotlin_stub_check` in the workflows). Deduction: see findings 1 and 2 |
| 5 | Protocol (2) | **2/2** | `tools/session_start_check.sh` ok (marker in the current round section); `tools/docs_claim_check.sh` green with the new skill inside its audited glob; session plan closed; six error entries written the moment the errors were hit; `user.md` dated |
| 6 | No stubs (1) | **1/1** | `check_subagents.py --self-test` rejects a broken copy on three independent defects; no placeholder token in any contract file; no member folder contains invented data |

## Findings (ordered by severity)

1. **The final critic is not an independent reviewer (major, and the reason for
   the withheld point).** `spawn_agents` refused
   `code-reviewer-multi-prompt`: *"Agent ... is not available to spawn"* — the
   environment only offers the web-research agent. So the grade above is the
   documented procedure (`critic-final/SKILL.md`: preflight, rubric, gate runs,
   evidence sampling) executed by the same agent that built the tree, not a
   second model's judgement. Mitigations that are real: the rubric is fixed in
   `ORIGINAL.md` before the work, the preflight is mechanical, and every verdict
   points at a command output. That is not the same as independence, and this
   review does not pretend it is.
2. **The evidence census is only partly triaged (minor).** `critic-evidence`
   leaves 72 capability-claim lines unreviewed (`PROPOSALS.md` CE-3). Declaring
   them fine without reading them would be exactly the guessing the member
   exists to prevent, so the count stays open — but it also means criterion 4 is
   satisfied for the proposals and the parent's claims, not for the whole
   documentation corpus.
3. **Reports are a snapshot (minor).** Each `PROPOSALS.md` names the run it came
   from. The last `run_all.py` ran after the record updates, so the numbers are
   current as of this review; a later edit to the tree makes them stale and the
   runner must be executed again before they are quoted.
4. **Six copies of a six-line loader (minor, accepted).** `_load_core` exists in
   every member script (`critic-architecture` CA-2). It is the price of the
   owner's requirement that every member have its own runnable script; the shared
   logic itself is single-sourced in `tools/codegraph_core.py`. Recorded so it is
   not re-filed.

## Fix list

None required: the score is above the 7/10 threshold. The three items that would
raise it to 10, in order of value:

1. Run the critic as a genuinely separate model when one is available, and keep
   this procedure as the machine-checkable half of it.
2. Triage the 72 open capability claims in batches, with the same `file:line`
   discipline.
3. Move the six `_load_core` copies behind one helper exposed by the shared core,
   if and only if each member's script stays runnable on its own.

## Method (reproducible)

```bash
python3 .subagents/tools/run_all.py
python3 .subagents/tools/check_subagents.py
python3 .subagents/tools/check_subagents.py --self-test
python3 .subagents/critic-final/codegraph.py --json reports/latest.json
bash tools/session_start_check.sh
bash tools/docs_claim_check.sh
/tmp/pf/bin/python -m pyflakes .subagents/tools/*.py .subagents/*/codegraph.py
```

All of the above were run in this session; the outputs quoted here are from
those runs.

---

# Re-review — 2026-10-29, round 13 (the five findings)

**Score: 9/10** — PASS, unchanged from round 12, and deliberately so: the five
findings are closed with evidence, but the two reasons the point was withheld are
not part of this round and are still open. Awarding 10/10 here would mean moving
the rubric to fit the result.

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | Structure (2) | **2/2** | `check_subagents.py` still 20 checks / 0 failures; preflight `folders ready: 6/6` |
| 2 | Skills (1) | **1/1** | unchanged frontmatter validation, all seven skill files valid |
| 3 | Code graph (2) | **2/2** | `run_all.py` 6/6 `rc=0`; reports describe 234 files, 62 `.md` |
| 4 | Evidence (2) | **1/2** | the five fixes each carry a probe (table below) and `gguf_test.py` is 101 checks / 0 failed — but the independence gap of round 12 is unchanged (no separate reviewer model is spawnable) and `critic-evidence` still lists 66 untriaged capability lines |
| 5 | Protocol (2) | **2/2** | round-13 section carries the R33 marker; six error entries from round 12 plus the new self-reference entry; `docs_claim_check` and `session_start_check` green |
| 6 | No stubs (1) | **1/1** | `--self-test` still rejects three deliberate defects; no placeholder tokens |

## Closure table

| ID | Finding | Closed by | Probe (run this session) |
|---|---|---|---|
| SV-1 | llama.cpp pin had no source | `AGENTS.md` cites the release page read 2026-10-29 | `grep -c "releases/tag/v0.5.0" AGENTS.md` → 1 |
| SC-1 | CRC known answer missing from the format doc | `docs/FORMAT-V2.md` states both known answers | re-run of `web-spec-conformance`: `0xCBF43926` no longer in the undocumented list (4 internal fixtures remain) |
| TS-1 | Kotlin stub gate in no workflow | `AGENTS.md` §3 declares it manual-only with the Gradle reason | `grep -c "Manual-only local gate" AGENTS.md` → 1 |
| CE-1 | hard-coded counts in the file that states R21 | all four replaced by parse instructions | `grep -c '109 checks\|34 checks\|43 live HTTP\|17 pairs' AGENTS.md` → 0 |
| CA-1 | `_decode_bf16` implemented twice | R9 comparison (65536 patterns, 0 mismatches) then `tools/bf16.py` | `grep -l "bf16.decode_bf16" tools/{gguf_reader,safetensors_to_hydra}.py` → both; `gguf_test.py` 101/0 |

## Findings

1. **A new instrument bug of the same class was found and fixed (major, closed in
   the same round).** The conformance census built its "documented" corpus from
   every Markdown file, including `.subagents/*/PROPOSALS.md` — so reporting a
   constant made it "documented". Detection: after the SC-1 fix the census claimed
   *zero* undocumented constants, including `0xdeadbeef`, which no format doc
   mentions. Fixed by excluding `.subagents/` from both the conformance and the
   evidence corpus. This is the second self-reference bug in two rounds; it is
   logged in `.agents/errors.md` as a class, not an incident.
2. **Criterion 4 remains at 1/2 (unchanged, not caused by this round).** The
   review is still produced by the same agent that wrote the code, and 66
   capability claims in the live docs are still untriaged (`critic-evidence`
   CE-3). Both were named in the round-12 review and neither was in this round's
   scope.
3. **The BF16 duplicate NAME survives by design (minor).** Both tools keep a
   two-line adapter that only re-types the error (`SafetensorsError` vs none), so
   the name-level duplicate check still prints one row. The rule — the
   conversion — now exists once.

## Fix list

None required (9/10 ≥ 7/10). To reach 10: run the critic as a separate model,
and triage the 66 remaining capability claims.

---

# Re-review — 2026-10-29, round 14 (threat-scan agent, R34/R35, CI gate, per-sub error/request files)

**Score: 9/10** — PASS (threshold 7/10). This is a **procedural** review: the
grader is this folder's script plus the repository gates, not an independent
model (none is spawnable in this environment — stated, not hidden).

## Criterion table

| # | Criterion | Points | Verdict | Evidence |
|---|---|---|---|---|
| 1 | Structure: 7 folders × `ORIGINAL.md`, `AGENTS.md`, `SKILL.md`, `codegraph.py`, `ERROR.md`, `REQUESTS.md`, `PROPOSALS.md`, `reports/` | 2 | met | `check_subagents.py` → `7 folders checked, 0 failure(s)` |
| 2 | Skills conform to the Agent Skills spec (strict YAML, spec keys, name==folder, description ≤1024 chars, body <500 lines, visible trigger) | 1 | met | same gate, parser line "PyYAML (strict, full YAML)"; 7 skills + the parent skill valid |
| 3 | Every `codegraph.py` runs and describes the real tree | 2 | met | `run_all.py` → 7/7 rc=0, first attempt; reports describe 257 files, 81 `.md`, 4 markers |
| 4 | Evidence: every claim has a command output, a `file:line` or a URL | 2 | met | `.agents/session.md` R14 results table; `reports/scan.json`; threat model with 30 URL lines |
| 5 | Protocol: R33 marker, records updated, English artefacts, gates green | 2 | **1 of 2** | R33 marker present, records updated, docs claim gate green — but the new CI job has not executed on a runner (see finding 1) |
| 6 | No stubs, no fake checkboxes, no invented data | 1 | met | gate has a placeholder scan **and** a size floor on `ERROR.md`/`REQUESTS.md`; `--self-test` rejects 7 deliberate defects |

**Total: 9/10.**

## What the round actually proved (not claimed)

- **End-to-end negative control on the real tree.** A probe file written to the
  repository root (tag-block payload, zero-width run, bidi override, hidden
  element with an exfiltration instruction, a secrecy sentence, `curl | bash`) <!-- ai-threat-scan: allow pipe-to-shell (quoted as the probe content, not a command to run) -->
  produced `5 high + 1 medium`, `VERDICT: FAIL`, **scanner exit 1**, with the
  hidden payload printed decoded (`6 tag characters, decodes to 'IGNORE'`). After
  deleting the file: **exit 0**. The gate is not decorative.
- **Rule proof before use.** `scan.py --self-test`: 27 fixtures fire, the clean
  file and the clean tree stay green, and both waiver forms (single and
  multi-rule) move a hit from `findings` to `waived`.
- **The scanner found its own bugs first.** 45 high findings on the first run,
  45 self-referential; every one of the six real defects (self-scan of source,
  self-scan of output, UI-attribute window, waiver parser, `.ps1` suffix,
  vocabulary) is logged in `.subagents/ai-threat-scan/ERROR.md` and
  `.agents/errors.md` with the change that followed.

## Findings

1. **The CI job is configured, not yet observed (the withheld point).** The job
   `ai-threat-scan` exists in `.github/workflows/lint.yml` and its YAML passes
   `workflow_yaml_check.sh` + `workflow_lint_check.sh`; its steps were run
   locally with the same commands (`--self-test`, tree scan, `run_all.py`, both
   gates, `pyflakes`, `bandit -s B610`). No GitHub runner has executed it,
   because this round does not push. Treat the job as *unproven on a runner*
   until a green run exists.
2. **The detector's own source is excluded (standing limit).** `scan.py` defines
   the patterns it searches for, so it is skipped; `--self-test` is the control
   for that blind spot. Documented in `.agents/docs/AI-THREAT-MODEL.md` §4, not
   papered over.
3. **21 low notes, 12 of them classified (minor).** Eleven are
   `public/index.html` UI attributes and one is the `display:none` marker in <!-- ai-threat-scan: allow hidden-with-instructions (the review names the property it discusses) -->
   `public/style.css` (classified in `PROPOSALS.md` P-5). The other nine are
   lines in documents that *name* the mechanism they document (`errors.md`, this
   review, the scanner's own `ERROR.md`/`PROPOSALS.md`/`REQUESTS.md`) - the
   weakness of proximity-based hidden-content detection, stated in the threat
   model §4. None fails the gate; the threshold question is `REQUESTS.md` R-1
   and is the owner's.

4. **No independent reviewer (standing limit, named again).** A 9/10 produced by
   a script and a rubric is evidence of a procedure, not a second opinion.

## Fix list

None required (9 ≥ 7). To reach 10:

1. Push the branch and observe the `ai-threat-scan` job green on a runner (owner
   authorization for the push; the rules forbid it without one).
2. Get the owner's answer on `REQUESTS.md` R-1 (keep `--fail-on high`, or move to
   `medium` once the low notes are classified) and R-5 (who may waive a `high`).

---

# Re-review — 2026-10-29, round 15 (self-scan blind spot closed, two paths resolved, gate re-proved)

**Score: 9/10** — PASS (threshold 7/10). Procedural review again: this folder's
preflight plus the repository gates, not an independent model.

## Criterion table

| # | Criterion | Points | Verdict | Evidence |
|---|---|---|---|---|
| 1 | Structure: 7 folders × 8 required files, plus a layout check for duplicate trees | 2 | met | `check_subagents.py` → 25 checks, 0 failures, incl. `layout: exactly one sub-agents directory` |
| 2 | Skills conform to the Agent Skills spec | 1 | met | strict PyYAML pass; the 7 member skills and the parent skill valid |
| 3 | Every `codegraph.py` runs and describes the real tree | 2 | met | `run_all.py` → 7/7 rc=0, first attempt |
| 4 | Evidence: every claim has a command, a `file:line` or a URL | 2 | met | session.md R15 table; `reports/scan.json`; the plant-detect-remove cycle is reproducible line by line |
| 5 | Protocol: R33 marker, records updated, English, gates green | 2 | **1 of 2** | all local gates green and the R33 gate is now stable (5 consecutive rc=0), but the CI job still has not run on a runner (finding 1) |
| 6 | No stubs, no fake checkboxes | 1 | met | gate placeholder scan + size floors; 8 deliberate defects rejected |

**Total: 9/10** — unchanged, and the withheld point is the same one: only a
runner can turn the CI job from "configured" into "observed".

## Closed since round 14

1. **The self-scan blind spot is gone.** Round 14 skipped `scan.py` as a whole
   file; round 15 removed that skip and waives 38 hits on 36 individual pattern/fixture
   lines with a written reason. The file is in the scanned count (233 includes
   it), and the `own_source` fixture copies the scanner, requires the copy to be
   clean, appends one hidden payload and requires it to be caught. Proved on the
   real tree: payload appended → exit 1, `[HIGH] invisible-tag-block …scan.py:605`,
   decoded `STEAL`; `sha256sum -c` OK; exit 0.
2. **The two paths are named and checked.** `.agents/skills/sub-agents/` is the
   procedure, `.subagents/` is the team; the split is in `.subagents/README.md`
   ("Two paths, two jobs") and in the gate (one `sub-agents` directory, no member
   files inside it, both sides name each other). A planted root-level
   `sub-agents/` turned the gate red on the real tree.
3. **`tools/bf16.py` is not an orphan.** Both converters import it
   (`tools/gguf_reader.py:41`, `tools/safetensors_to_hydra.py:82`), and it is
   documented in `README.md:358` and `AGENTS.md` §2.3.

## Findings

1. **The CI job is still configured, not observed (the withheld point).** Its
   YAML parses (PyYAML, job `ai-threat-scan`) and its step order is asserted:
   self-test at step 3 before the tree scan at step 4, `--fail-on high` on the
   scan, reports before the gate, gate before its own control. No runner has
   executed it, because this round does not push.
2. **The scanner's own 38 waivers are maintained by hand (minor, open request).**
   They are narrow today and `own_source` pins the property, but nothing forces a
   *future* waiver to sit on a pattern or fixture line. `REQUESTS.md` R-6 proposes
   the mechanical check; it is not implemented, so it is a limit, not a claim.
3. **21 low notes remain, all classified** (11 UI attributes, 1 UI CSS marker,
   9 lines in documents that name the mechanism). None fails the gate; the
   threshold question stays with the owner (`REQUESTS.md` R-1).
4. **The session-start gate was flaky and is now deterministic.** Found while
   re-proving: `grep -q` at the end of a `pipefail` pipeline turned a successful
   match into a red gate by SIGPIPE. Fixed in `tools/session_start_check.sh`;
   5 consecutive runs rc=0, in-script negative control still rejects a section
   without the marker.

## Fix list

None required (9 ≥ 7). To reach 10: push and observe the `ai-threat-scan` job
green on a runner (owner authorization), and decide `REQUESTS.md` R-1/R-5.

## Round 16 — the waiver is now bounded, and the bound is proven

**Score: 9/10** — PASS (threshold 7/10). One point withheld for the same reason as
round 15, plus one new limit named below; both are stated, neither is hidden.

Reviewed: `scan.py` (waiver grammar, `_add`, `_reason_ok`, `_waiver_note`), the new
self-test fixtures, `.subagents/ai-threat-scan/AGENTS.md` ("The waiver rule"),
`.agents/docs/AI-THREAT-MODEL.md` §3.1, `REQUESTS.md` R-6, the round-16 entries in
`.subagents/ai-threat-scan/ERROR.md` and `.agents/errors.md`.

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | Structure (2) | **2/2** | `check_subagents.py`: 25 checks, 0 failures; seven folders with the required files; layout check still rejects a duplicate `sub-agents` tree (`--self-test`, 8 defects rejected) |
| 2 | Skills (1) | **1/1** | unchanged this round; strict PyYAML parse green, seven skills with `## When to use` |
| 3 | Code graph (2) | **2/2** | `run_all.py` 7/7 `rc=0`, first attempt |
| 4 | Evidence (2) | **1/2** | plants A/B inside `scan.py` (exit 1 with the file named, decoded payload printed) and plant C in an ordinary file; byte-identical restore via `sha256sum -c`; two mutation controls (`_reason_ok` → true, ids widened to every rule) each turn the self-test red. Withheld: the CI job is still only run locally - no runner was observed because this round does not push |
| 5 | Protocol (2) | **2/2** | session-start marker present; docs-claim check green; four real mistakes recorded with root cause (including the error entry that quoted the phrase and turned itself red) |
| 6 | No stubs (1) | **1/1** | no placeholder text; every claimed number comes from a run in this round |

**Findings.**

1. **The waiver can no longer hide an unrelated hit.** Exact rule id plus a reason of
   at least 20 characters, otherwise nothing is suppressed; a marker that names a
   known rule but has no usable reason leaves the finding and adds one
   `waiver-invalid` low note at that line. The note is appended directly and cannot
   be waived, so the failure mode "my waiver silently stopped working" is gone.
2. **The inventory is the proof of what was hidden.** 46 entries on 42 lines, each
   with rule, `file:line` and the written reason, in the text report and in
   `--json`; shortest reason 24 characters.
3. **No waiver region was added, deliberately** (`REQUESTS.md` R-6). A line map
   would drift and would reject legitimate quotes; the semantic bound rejects the
   same cases on the current tree and is pinned by six fixtures instead of a
   hand-maintained range.
4. **Still not proven:** a green `ai-threat-scan` job on a CI runner. The workflow is
   parsed with PyYAML and the step order (self-test before tree scan) is asserted
   programmatically, but the job has not executed on GitHub. That needs a push,
   which is the owner's call.

## Fix list

None required (9 ≥ 7). To reach 10: observe the job on a runner, and settle
`REQUESTS.md` R-1 (severity threshold) and R-5 (who may approve a `high` waiver).

## Round 17 — coverage audit, three new detectors, and a self-test that can no longer pass by accident

**Score: 9/10** — PASS (threshold 7/10). The withheld point is the same one as
rounds 15-16: no CI runner was observed, because this round does not push.

Reviewed: `.subagents/ai-threat-scan/scan.py` (decoders, de-confusion, PUA,
`LOOP_RULES`, self-test assertions), `codegraph.py` (drift set), the coverage
matrix in `AGENTS.md`, `.agents/docs/AI-THREAT-MODEL.md` §3/§3.0/§4, the round-17
entries in `ERROR.md` and `.agents/errors.md`.

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | Structure (2) | **2/2** | `check_subagents.py`: 25 checks, 0 failures; seven folders complete |
| 2 | Skills (1) | **1/1** | strict PyYAML parse green, no skill touched this round |
| 3 | Code graph (2) | **2/2** | `run_all.py` 7/7 `rc=0`; `ai-threat-scan` report row shows self-test ok, rule drift none, tree 233/0 high |
| 4 | Evidence (2) | **1/2** | every new rule has fixture + mutation control + a real plant-detect-remove cycle; `sha256sum -c` 242/242. Withheld: the CI job is still only run locally |
| 5 | Protocol (2) | **2/2** | plan written before the first edit; five real mistakes recorded with cause (self-test couldn't see a missing fixture, stale drift copy, hand-derived count, useless waiver, dead counter) |
| 6 | No stubs (1) | **1/1** | no placeholder code; all numbers from this round's runs |

**Findings.**

1. **Three classes were genuinely undetected and now are**: `encoded-instruction`
   (base64/hex/percent/ROT13 that decodes to secrecy/override language),
   `homoglyph-instruction` (Cyrillic/Greek look-alikes, fires only when
   de-confusing creates the match), `private-use-character` (low, informational).
   30 detection rules, one fixture each.
2. **The self-test was weaker than it looked.** It asserted "some rule fired
   somewhere" and two rules had no fixture at all. It now asserts per file, per
   rule id and per line, compares the fixture set with `rules_table()` (set and
   count), checks `LOOP_RULES` for orphans/ghosts, and keeps six near misses clean.
3. **False-positive discipline is measured, not claimed**: 25 legitimate Greek
   math tokens in this tree, 0 private-use characters, and the tree scan stays at
   the same 21 low notes as before the new rules (all UI/doc residue from earlier
   rounds). A bare mixed-script token is deliberately not flagged.
4. **Still not proven:** a green `ai-threat-scan` job on a GitHub runner. The
   workflow parses and the step order is asserted with PyYAML, but the job has not
   executed. That needs a push, which is the owner's call.
5. **Backlog is explicit**, not implied: multi-layer decoding, homoglyphs outside
   the built-in table, payloads in binaries, and instruction in visible code
   comments are listed as NOT covered with the reason each (`AGENTS.md` matrix +
   `.subagents/TODO.md`).

## Fix list

None required (9 ≥ 7). To reach 10: observe the job on a runner; settle
`REQUESTS.md` R-1 (severity threshold) and R-5 (who may approve a `high` waiver).

## Round 18 — nested encodings, comment-form instructions, and two design mistakes caught by their own controls

**Score: 9/10** — PASS (threshold 7/10). Withheld point unchanged: no CI runner was
observed, because this round does not push.

Reviewed: `scan.py` (iterative decoder, `COMMENT_BODY`/`AGENT_ADDRESS`, fixtures),
`AGENTS.md` coverage matrix delta, `.agents/docs/AI-THREAT-MODEL.md` §3/§3.0/§4,
round-18 entries in `ERROR.md` and `.agents/errors.md`, `PROPOSALS.md` P-11/P-12.

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | Structure (2) | **2/2** | `check_subagents.py` 25 checks, 0 failures; seven folders complete |
| 2 | Skills (1) | **1/1** | strict PyYAML parse green; no skill changed |
| 3 | Code graph (2) | **2/2** | `run_all.py` 7/7 rc=0; rule drift row: declared 32, unused none |
| 4 | Evidence (2) | **1/2** | nested chain quoted from a real run (`base64->rot13 … depth 2`), two mutation controls, plant-detect-remove with 242/242 `sha256sum -c`. Withheld: still no runner |
| 5 | Protocol (2) | **2/2** | plan before edit names the closed and the refused rows with measurements; two real mistakes logged with cause (self-referential `<!--`, over-loose address anchor) |
| 6 | No stubs (1) | **1/1** | no placeholder paths; every number from this round's runs |

**Findings.**

1. **Multi-layer encoding is now real detection**, not a widened regex: iterative
   decode to depth 3, 4096-char cap, `seen` set against loops, and the finding names
   the chain and depth. `base64(rot13(instruction))` exits 1; the harmless nested
   near miss stays clean.
2. **Comment-form instructions are covered in the addressed shape only.** The broad
   shape was measured at 54 legitimate lines in this tree before being rejected -
   the number is in the matrix, so the next agent sees why the rule is narrow.
3. **The self-test earned its keep twice.** The own-source control caught a literal
   `<!--` in a new regex that made the scanner read its own SECRECY table as a hidden
   HTML comment, and the required near-miss caught an address pattern that would
   have flagged quoted examples.
4. **Backlog is now honest and small**: deeper-than-three-layer encodings, unknown
   ciphers, homoglyphs outside the table, binary payloads (counted in every report),
   typoglycemia, prose intent. Each with a concrete next step.
5. **Still not proven:** the `ai-threat-scan` job on a GitHub runner, and binary
   payloads are not decoded by design.

## Fix list

None required (9 ≥ 7). To reach 10: observe the job on a runner; settle
`REQUESTS.md` R-1 and R-5.
