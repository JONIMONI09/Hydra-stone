# Session Log — Hydra-Stone

> Protocol: see `.agents/skills/session-workflow/SKILL.md`.
> This file is updated at session start, after every completed step,
> and at session end. Read it BEFORE touching code.

## Done (previous sessions)

- ✅ **2026-10-01 — Engine from spec (PR #1, merged):** Implemented the
  Hydra-Stone C99 engine from the original technical spec: mmap-based
  zero-heap weight streaming, 2-bit ternary weights, coexistence-axiom
  gate, hardening, 16 unit tests, docs, CI. Reviewed afterwards;
  review findings tracked.
- ✅ **2026-10-01 — Review fixes + Web console (PR #2, merged):** Fixed
  OOB read (`layers*dim > weights_len` validation), clean state
  clamping, logs to stderr; added zero-dependency Node web console
  (`make ui`), `--json` CLI mode.
- ✅ **2026-10-01 — Real tests (PR #3, merged):** Replaced tautological
  tests with hand-computed decoder cases + seeded LCG roundtrip/variance
  tests (32 tests total, platform-fixed LCG).
- ✅ **2026-10-01 — NEON integration (PR #4, merged):** Kernel now
  genuinely wired into `step()` (was dead code); scalar fallback fixed
  on x86; honest SIMD docs. A dispatch bug was caught by the variance
  test before merge.
- ✅ **2026-10-01 — English docs (PR #5, merged):** All `.md` rewritten
  professionally in English; honest density limitation documented.
- ✅ **2026-10-01 — Android NDK port (PR #6, merged):** APK builds for
  arm64-v7a/arm64-v8a/x86_64 via CMake+JNI; verified end-to-end on an
  API-24 x86_64 emulator (no KVM). 7 errors hit and fixed — full log in
  `errors.md`, guide in `.agents/docs/ANDROID_SKILL.md`.
- ✅ **2026-10-01 — CI lint stage (PR #7, merged):** Dual-compiler
  syntax gates (gcc+clang), cppcheck, Python format gate,
  error-artifact upload. cppcheck caught a real `%u`/signed issue on
  first run.

- ✅ **2026-10-02 — Bugfix audit (PR #11, merged by user):** NEON sign
  inversion (PoC: x86 `211,388,...` vs. ARM `211,28,...`) and layer
  overflow (UB) fixed, plus 12 further findings; `test_neon_matches_scalar`
  compares NEON and scalar **in the same build** and immediately found a
  second, latent lane-offset bug. 49 tests x86 / 51 ARM. **[historical,
  superseded]** — those counts were true on that date; the suite has grown
  since. The current counts are parsed from the test binaries by
  `tools/test_count_check.sh` (see `tools/test_count_baseline.txt`), never
  written down here.
- ✅ **2026-10-02 — Web console, skills, Android APK:** see
  "Done (earlier today)" and `.agents/docs/ANDROID_SKILL.md`.

## Done (earlier today)

- ✅ Skills created + protocol files (PR #8, merged by user)
- ✅ Frontmatter v1 added (PR branch), then hardening (ASCII + quoted,
  **PR #9, merged by user at 15:46:21Z**) — main now serves valid
  skills; user invoked `/android-ndk-build` successfully → skills work
- ✅ Skill optimization after a verified end-to-end run (PR #10, merged
  by user)
- ✅ All PRs from that line are now closed: #7–#14 merged

### CI fix round (2026-10-03)

- [x] **Blocking CI failure fixed at the root.** `AssertionError: a longer
      prompt must change the output` was **not** a prompt bug: the starter
      model had `B[0] == 0`, so the decoder's `acc[0] = A[0]*token +
      B[0]*state[0]` dropped the state term entirely and prefill could not
      possibly change the output. `tools/make_model.py` now guarantees
      `A[0] != 0` and `B[0] != 0` by construction and asserts it. Verified:
      seed 5 → `[11, 33, 109]` vs `--prompt 1,5` → `[13, 41, 137]`.
- [x] **The starter model is no longer a degenerate cycle.** It emitted
      `471, 42, 471, 42` forever; it now emits
      `471, 386, 385, 386, …` - the recurrence actually contributes.
- [x] **`bench_run` initialised its out-parameter on every path** (real
      uninitialised read, only masked by statement order in the caller).
- [x] **`sscanf` → `strtoul`** for `/proc/self/statm`; a malformed line used to
      report a plausible `0 KiB` instead of "unknown".
- [x] **`bugprone-easily-swappable-parameters`**: the three mutually-convertible
      scalars (`start_token`, `steps`, `mode`) are now a `BenchRequest` struct
      passed by pointer. An enum was tried first and did **not** work — C enums
      are still implicitly convertible to every integer type, so the check
      still fired. Verified with CI's *exact* `--checks` list and file set,
      which is what the first (falsely green) local run had omitted.
- [x] clang-tidy + clang Static Analyzer: **0 findings**.
- [x] ASan+UBSan clean on the suite (71) and on the CLI bench path.
- [x] Cross-platform determinism re-verified on the **new** model across three
      targets: x86-64 host, ARM64/NEON under qemu, and the x86_64 emulator all
      emit `[471, 386, 385, 386, 385, 386, 385, 386]`.

## Round 2026-10-26 (round 6: CI red fix, local Kotlin type-check, .agents/ reorg — owner request)

**Owner request (verbatim):** "CI ist rot! :(" — fix it; "Teste alles lokal
mit Python"; "Immer Internet benutzen" + install missing tools (pip/npm);
move all agent-specific docs into a new `.agents/` folder (README.md and
AGENTS.md stay at root); add Rules etc. there; improve the agent files;
create a user-rules file (`.agents/user.md`); read `.agents/` before any
code, update it at the end of the round; adjust Environment.md.

### Root causes of the red CI (main f79ff96, all four workflows)

1. **CI job 1c (cppcheck):** `uninitvar` ×2 — `tests/test_engine.c:2790-91`,
   the v3 report roundtrip test's `hx[16]`/`hy[16]` were passed to
   `hydra_engine_report()` before cppcheck could prove a per-iteration
   write. Fix: zero-init `= {0}` (codebase convention for
   incrementally-filled buffers).
2. **Lint & Security "Android lint" + Release "Android APK" + CI Android
   jobs:** `HydraApp.kt:1011` — round-5 `SettingSlider` took
   `valueRange: ClosedFloatingPointRange` and used `.last`/`.first`, which
   only exist on IntRange. Found via check-run annotations
   (`gh api .../check-runs/<jobId>/annotations`) because the job logs and
   artifacts are blob-blocked from the sandbox. Fix: the slider takes
   `start: Float, end: Float` + step; step count from the span; the 6 call
   sites converted.
3. **Code-scanning workflow: corrupted GitHub registration.** The workflow
   was registered 2026-10-26 with the file PATH as its name and a broken
   trigger set: it ran on EVERY push (runs #20-#22, event=push, 0 jobs,
   fails in <3s, no logs — the "zero-job" signature). The file itself is
   valid YAML (PyYAML + the repo's duplicate-key gate both clean). Fix:
   force a fresh registration by moving it to
   `.github/workflows/code-scanning-alert.yml` (same content, same
   `name: Code scanning alert handling`). After the merge, the old
   registration (path `code-scanning.yml`) is orphaned by the deletion and
   the new path registers from the known-good content.
4. **clang gate 1b: `-Wtypedef-redefinition` in hydra_model.h (C99).**
   `hydra_kv_cache_t` was typedef'd twice (forward at line 153 + repeated
   on the full definition at line 287) — legal in C11, a warning under
   clang `-std=c99` → `-Werror` red. GCC is silent (its diagnosis sits
   behind `-Wpedantic`), which is why every local gcc gate stayed green.
   Introduced in round 4, merged in PR #57; the "lint" job of ci.yml was
   red on main since the merge (timeline: 12:11 green, 13:37+ red).
   Fix: full definition is now a plain `struct hydra_kv_cache { … };`
   (the name stays bound by the forward declaration). Diagnosed by
   reproducing gate 1b locally with `zig cc -target x86_64-linux-gnu`
   (zig bundles a Clang frontend — new local capability, see
   Environment.md round-6 item).
5. **Kotlin `weight` — a false alarm, corrected after CI's K2 error.**
   The local stub check flagged `Modifier.weight(1f)` (×5) as
   unresolved; the first "fix" added
   `import androidx.compose.foundation.layout.weight`. CI's K2 compiler
   rejected the import: `Cannot access 'val RowColumnParentData?.weight:
   Float': it is internal in file`. Real API (Compose source,
   RowColumnImpl.kt): `weight` is a member extension of RowScope/
   ColumnScope — resolvable inside the scope lambdas, import forbidden.
   The import was removed (the round-5 code was right on this point);
   the stub now declares `weight` as scope members, faithfully rejecting
   the import form. Full story in `.agents/errors.md`.

### The local Kotlin type-check (the capability this round added)

No Android SDK is possible in the sandbox (Maven blocked), but the Kotlin
COMPILER is on the npm registry:
`npm install kotlin-compiler@2.4.21 javajre-linux-64@17.0.8` (kotlinc-jvm
2.4.21 on JRE 17.0.8, matching the CI Temurin 17 major). Built a faithful
stub classpath (`tools/kotlin_stub_check/stubs/`, 40 files: android.*/
androidx.*/compose/org.json + R generated from the real strings.xml) and a
runner: `bash tools/kotlin_stub_check/kotlin_stub_check.sh` → compiles all
10 app .kt files in ~20s. This caught root cause #2 locally, before CI. Verified: **0 errors** on the fixed tree
(only 3 warnings, 2 pre-existing redundant-`else`, 1 stub artifact).
Stub-fidelity rules learned (see `.agents/errors.md`): verify API
signatures on the web before stubbing (Compose `items` key lambda is
single-parameter `(item: T) -> Any` — the two-parameter one is
`itemsIndexed`; `weight` is a scope MEMBER, not a top-level
extension); one package per stub file; fun-interface for Java SAMs;
JVM signature clashes when stubbing var+fun pairs. A stub error means
app code OR stub is wrong — the real API is the tie-breaker (the
`weight` episode proved it in both directions).

### .agents/ reorg (owner directive)

Moved (git mv): rules.md, errors.md, session.md, Environment.md, CLAUDE.md
→ `.agents/`; docs/{ANDROID-AUDIT,ANDROID_SKILL,RESEARCH,
HYDRA2-RESEARCH,gpu-feasibility,pr-gpu-feasibility}.md → `.agents/docs/`;
`.agent_memory/` → `.agents/docs/{TECHNICAL-AUDIT,RESEARCH-LOG}.md`
(folder deleted). Root keeps README.md + AGENTS.md; `docs/` keeps the
product specs (FORMAT.md, FORMAT-V2.md, GGUF-IMPORT.md, ARCHITECTURE.md).
All path references updated repo-wide (44 files, incl. CI comments, tools,
code comments, AGENTS.md pointer table); `tools/docs_claim_check.sh` FILES
array extended with `.agents/docs/*.md` (gate still passes). New:
`.agents/user.md` (owner's standing directives, dated, 21 entries) and
`.agents/README.md` (index + maintenance rules). Historical CHANGELOG
entries keep their dated old paths on purpose.

### Verification (all local, real outputs)

- `make test-run`: 174/0 + 86/0 + 7/0 + 73/0 (unchanged).
- cppcheck (venv, --enable=all -Isrc -Itests): 0 issues.
- `tools/kotlin_stub_check/kotlin_stub_check.sh`: OK (0 errors).
- `bash tools/docs_claim_check.sh`: all banned claims absent.
- `bash tools/workflow_yaml_check.sh`: 6 files parsed, negative control ok.
- `python3 tools/string_format_check.py`: ok (39 checked).
- PyYAML full parse of all 5 workflows: clean (installed via pip — the
  stdlib-only fallback in workflow_yaml_check.sh cannot see syntax
  errors; it passed, so the rename risk is covered by both).
- **clang gate-1b replica (local, new):** `zig cc -target x86_64-linux-gnu
  -std=c99 -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE -Wall -Wextra
  -Werror` on all 5 CI files → reproduced the #4 failure before the fix,
  5/5 clean after.
- **NEON path after the header change:** `zig cc -target aarch64-linux-gnu`
  full compile of both src files → rc 0.

**Files:** tests/test_engine.c, include/hydra_model.h, android/app/src/
main/java/dev/hydrastone/ui/HydraApp.kt (weight import removed — false
alarm), tools/kotlin_stub_check/ (new; stubs corrected for scope-member
weight), .agents/ (new folder: 5 moved files + 8 moved docs + user.md +
README.md), .github/workflows/code-scanning.yml →
code-scanning-alert.yml, 44 reference updates.

**Open (superseded by follow-up 2 below):** PR #59 open. After merge:
confirm no zero-job push runs and all four workflows green on main —
see follow-up 2 for what the forensics actually showed.

### Round-6 follow-up (after the first PR #59 CI round, 2026-10-26)

Two more reds surfaced in the first CI round of PR #59 and were fixed
the same day (commit after 303b5c8):

1. **Android lint job: gate crash + 2 real findings.** With the Kotlin
   compile finally fixed, the job reached the lint analysis for the
   first time in the repo's history. The annotation step crashed parsing
   the `.txt` report as XML (see errors.md) — hiding the findings.
   Real findings identified by resource audit: `models_empty_title` /
   `models_empty_body` unused (UnusedResources) — the models-tab empty
   state had never been implemented. Fix: implemented the empty state in
   `ModelsTab` (uses both strings, `model_none` placeholder removed from
   strings.xml, R stub regenerated: 105 strings + 6 plurals) and fixed
   the gate to parse the XML report with text/gradle-died fallbacks and
   best-effort annotation (R25: the gate must always report its
   findings).
2. **`Modifier.weight` import removed** (see root cause 5 in the list
   above — K2 rejects the import; real API = scope member, no import).
3. **clang gate 1b fixed** (hydra_model.h typedef redefinition, root
   cause 4 above) — verified in CI: the `lint` job of ci.yml turned
   GREEN on the PR after the fix.

Status after the second CI round: ci.yml `lint` PASS, all fast checks
PASS; Android lint was re-running with the fixed gate — its
annotations are the source of truth for any remaining findings.

### Round-6 follow-up 2 (third CI round, 2026-10-26 evening)

1. **The fixed gate worked — it published its first findings** (run
   40339750614): exactly two, both fixed in **3354a9f**:
   `AutoboxingStateCreation` at `HydraApp.kt:994` (`mutableStateOf`
   with a Float → `mutableFloatStateOf`, stub gained the matching
   top-level function) and `PluralsCandidate` at `strings.xml:143`
   (`log_context_applied` "%d tokens" → `<plurals>` with one/other;
   call site MainActivity.kt:658 → `R.plurals.…`; R stub
   regenerated: 104 strings + 7 plurals). Stub check 0 errors,
   string-format check ok.
2. **Code-scanning forensics finished:** the rename did NOT clear the
   old registration — BOTH (`code-scanning.yml` id 396960786,
   `code-scanning-alert.yml` id 397125007) are still `active` and both
   carry the file PATH as name (unique to these two; all other
   workflows show their real `name:`). The new name produced the same
   phantom zero-job runs, auto-retried by GitHub every ~13 min
   (13:59/14:12/14:26 — not our pushes). The loop stopped by itself
   after 14:26; nothing in the following 45+ min. `DELETE
   .../actions/workflows/{id}` is 404 (token scope) — if it wakes up,
   the owner must delete the stale workflow in the GitHub web UI.
   **Not blocking the PR** (push-event runs never appear in `gh pr
   checks`).
3. **Sandbox reset incident:** the local branch pointer came back at
   f79ff96 while all four commits lived only on the remote; worktree
   intact. Recovered with `git fetch` + mixed `git reset
   origin/arena/ed8432d1-bestai` (pointer + index only, worktree
   untouched → clean). New rule (errors.md): after every push-ending
   turn, verify `git log --oneline -1` == last pushed sha at the start
   of the next turn. `/tmp` also wiped — kotlinc reinstalled from the
   Environment.md recipe (~1 min).

**Open (superseded by follow-up 3 below):** PR #59 open, branch head
3354a9f.

### Round-6 follow-up 3 (fourth CI round + root-cause correction, 2026-10-26 evening)

1. **ROOT CAUSE CORRECTION — the "corrupted GitHub registration" theory
   was WRONG.** The phantom zero-job runs (0 jobs, same-second failure,
   run named by the file PATH) were **compile failures of any workflow
   file naming `on: code_scanning_alert`**: that event is a Webhook
   event, NOT a GitHub Actions workflow trigger event (not in the
   current docs trigger list — page runs `check_suite` → `create` with
   no such section — and actionlint rejects it: `unknown Webhook
   event`). Proof by causality: the phantom always named the file
   containing the bad event, and followed it across three commits
   (`code-scanning.yml` 13:37-13:53 → `code-scanning-alert.yml`
   13:59-15:11 → `lint.yml` 15:13, the latter after I moved the trigger
   in — where it again produced the zero-job failure AND the Lint&Sec
   PR run went missing). The `name` = path display and the 14:12/14:26
   "auto-retries" were red herrings (no `name:` to show on a
   compile-failed run; more dispatch attempts of the same broken file).
   PyYAML/the duplicate-key gate cannot see this: they validate YAML,
   not the Actions event schema.
2. **Action:** (a) deleted `.github/workflows/code-scanning-alert.yml`
   (1b0ace5); (b) reverted the `code_scanning_alert` trigger + alert
   job out of lint.yml; (c) NEW GATE 1i `tools/workflow_lint_check.sh`
   = actionlint (npm WASM build, `/tmp/al` self-recreating, one fresh
   node process per file — the WASM runtime crashes intermittently on
   multi-file processes) over every workflow file + in-gate negative
   control `tools/fixtures/workflow_lint_bad.yml` (the invalid trigger
   event itself; R25). Wired into ci.yml after gate 1h. Code-scanning
   REACTION stays native: CodeQL/Semgrep jobs report on every PR
   (annotations + check results) and alerts close themselves as fixed
   when the next default-branch analysis no longer reports them.
3. **Android lint round 3 (run 40346890465, 3354a9f):** both original
   findings cleared; the plurals conversion introduced ONE new finding
   — `MainActivity.kt:658 ResourceType: Expected resource of type
   string`: `Context.getString` does not accept `R.plurals.*`
   (`@StringRes` vs `@PluralsRes` is enforced by LINT, not kotlinc —
   the stub check cannot express resource annotations and stayed
   green). Fix: `getQuantityString(R.plurals.log_context_applied,
   new.contextSize, new.contextSize)`; stub `A_content.kt` gained
   `getQuantityString`; stub-check README gained a KNOWN-LIMITATIONS
   section (ResourceType / AutoboxingStateCreation / PluralsCandidate /
   UnusedResources / Compose transforms are CI-lint-only classes).

**Open (superseded by follow-up 4 below):** PR #59 open, fix commit
7c534b2 pending.

### Round-6 follow-up 4 (merge/revert incident + stage-2 API fix, 2026-10-26 evening — new session branch `arena/72470567-bestai`)

1. **Incident:** PR #59 was merged by the owner at 15:15:21 at head
   **1b0ace5** (the broken state — bad `code_scanning_alert` trigger in
   lint.yml; the fix commit 7c534b2 landed 3.5 min later, after the
   merge). Main went red immediately (zero-job compile-failure run of
   lint.yml). 16 s after the merge the owner opened **PR #60 (full
   revert of #59)** out of the red; the owner then CLOSED #60 and asked
   for "everything correct" to land (PR #62 was opened from
   `arena/ed8432d1-bestai` carrying exactly 7c534b2).
2. **PR #62 CI exposed stage 2 of the plurals fix:** all jobs green
   except Android lint — `MainActivity.kt:658:25 Unresolved reference
   'getQuantityString'`: **`Context` has no `getQuantityString`**, it is
   a `Resources` method (API 1, developer.android.com pattern
   `context.resources.getQuantityString(R.plurals.…, count, count)`).
   The stage-1 fix had added a fabricated `Context.getQuantityString`
   to the STUB (violating the "never guess stub members" rule) — the
   stub check passed, the real compiler failed. Final fix on this
   branch: `resources.getQuantityString(R.plurals.log_context_applied,
   new.contextSize, new.contextSize)` (the pattern the codebase
   already used at 395/536/796), fabricated Context stub member
   removed, errors.md entry expanded with the stage-2 lesson.
3. **State:** this session branch = main (0ad01dd) + 7c534b2 + the
   stage-2 fix. PR #62 (old branch) is red and should be CLOSED; the
   green vehicle is the new PR from this branch. Stale workflow
   registrations (396960786/397125007) remain listed but inert (no file
   at the path = no dispatch); PAT cannot delete them (404), owner can
   via the web UI.
## Follow-up after the merge (2026-10-26)

- [x] **Root cause of ALL zero-job phantom runs (2026-10-25 → 26):** `on: code_scanning_alert` is a Webhook event, NOT a workflow trigger event. GitHub's workflow compiler rejects a file that names it — the run is created with zero jobs, fails in the same second, and the run NAME is the file path. PyYAML (gate 1h) could never see this (valid YAML; the event name is a string).
- [x] **Fixed in gate 1i (new):** `actionlint` over every workflow file (npm, /tmp, ephemeral re-setup) + in-gate negative control. `bash tools/workflow_lint_check.sh` locally. ci.yml + lint.yml no longer name `code_scanning_alert`; auto-close policy unchanged (the alert workflow remains, its trigger is `check_suite`).
- [x] **Cherry-pick of 7c534b2 + the stage-2 fix + the root-cause docs shipped as PR #64** (arena/72470567-bestai): PR checks 15 pass / 4 skipped / 0 fail; Android lint green; both branch workflows success; zero phantom runs.
- [x] **PR #62 opened** (arena/ed8432d1-bestai, head 7c534b2): same content minus the stage-2 correction — its CI red = the stage-2 error itself, now fixed in #64. To be closed as superseded (owner merges).
- [x] errors.md + session.md + Environment.md updated; gate sweep green (workflow-yaml, actionlint + neg control, docs-claim, string-format, kotlin stubs, shellcheck); PR body facts-only.

**Status (2026-10-26 15:33):** PR #64 MERGED → main 19df869 (the PR tier is now fully green for the first time: build/test/neon + every lint gate). Remaining item: close PR #62 as superseded — done in round 7.

## Round 2026-10-26 (round 7: rule adaptation + .agents/ skills + all-.md audit)

**Session start (R33):** 2026-10-26 (branch `arena/e28fb029-bestai`, base main 19df869 = merged PR #64, all checks green). Read before touching code: AGENTS.md (full) → session.md (current round) → errors.md (top 3 entries) → rules.md (R1–R33, §6–§8) → user.md (5 owner rules + dated directives) → Environment.md (Arena section) → engine-ci-verify + ci-triage SKILL.md. Web research for the R33 root-cause question (2026 sources; only-enforcement-guarantees + context-dilution findings recorded under the R33 rule and in errors.md).

**Owner directives (2026-10-26, verbatim intent):**
1. „Passe deine Regeln an, du liest nie diese vorher“ — the read-`.agents/`-before-work rule kept being SKIPPED; adapt the rules so it reliably happens, and investigate why (2026 web research on agent context engineering).
2. „in .agents Ordner bitte mit skills füllen, lese dafür die, die auch wirklich in Claude Ordner sind“ — fill `.agents/` with skills; base them on the skills that really exist in `.claude/skills/`.
3. „Verbessere alle .MD Dateien suche alle .MD Dateien, in jedem Ordner“ — find and improve EVERY .md file in every folder.
4. „PR #62 was ist damit?“ — PR #62 is the red leftover of the #59-merge incident, superseded by the now-merged #64 → close it.

**Context:** PR #64 merged green at 15:33 (main 19df869 = stage-2 plurals fix + root-cause fix + gate 1i). PR #62 still OPEN (superseded). This round fixes the PROCESS (rules/skills/docs), not engine code.

**Diagnosis of the skipped reads (2026 sources, see R33):** (a) prose-only rules are followed probabilistically — "instructions raise the probability, only enforcement guarantees it" (prompt-architects, 2026); (b) context dilution — the root instruction file is loaded on EVERY request and a 2400-line session.md buries the protocol; (c) arXiv May-2026 study (1650 Claude Code sessions): compliance odds drop ~5.6% per additional function in the instruction set, file position/size had no effect → the fix is a verifiable marker + a gate, plus slimming.

**Plan:**
- [x] R33 added to rules.md (mandatory session-start read order + `**Session start (R33):**` marker in the current round section BEFORE the first code edit) + CI gate `tools/session_start_check.sh` (deterministic check of session.md + in-gate negative control per R25), wired into ci.yml as gate 1j.
- [x] `.agents/skills/` created as the CANONICAL skills home (2026 Agent Skills spec: name == dir, quoted description, what+when): the 3 skills moved out of `.claude/skills/` (git mv), `.claude/skills` is now a symlink to `../.agents/skills` (Claude discovery keeps working; R30: all agent docs live in `.agents/`).
- [x] 4 NEW skills (written from verified repo knowledge only, no invention): `ci-triage` (annotation-reading, zero-job signature, local gate replicas), `kotlin-stub-check` (setup/run + the stub-fidelity rules learned in rounds 5–6), `android-lint-gate` (annotation reading, lint-only classes ResourceType/PluralsCandidate/AutoboxingStateCreation/UnusedResources, correct APIs), `repo-docs-audit` (this round's audit made repeatable).
- [x] session.md slimmed: everything before round 6 moved verbatim to `.agents/docs/SESSION-ARCHIVE.md` (context-dilution fix; nothing deleted).
- [ ] All-.md audit (28 files listed in Workspace): stale paths, dead refs (deleted code-scanning workflow, old PR states), banned claims, R31 language.
- [ ] errors.md entry (skipped-reads → R33 + this round's findings); user.md entry for the 4 directives.
- [ ] Close PR #62 (superseded by merged #64; #62 CI red = the stage-2 error #64 fixed).
- [ ] Gates green (incl. new 1j), commit, push, PR (facts-only; owner merges).

**Progress:**
- [x] F1 — the pin is sourced (page read 2026-10-29) and the enforcing gate is
      named; probe: `grep -c "releases/tag/v0.5.0" AGENTS.md` → 1.
- [x] F2 — CRC known-answer pair in `docs/FORMAT-V2.md`; the conformance check
      no longer lists `0xCBF43926` (4 internal constants remain, as documented).
- [x] F3 — `kotlin_stub_check.sh` is a stated manual gate in `AGENTS.md` §3 with
      the Gradle evidence for why CI does not need it; the wiring check keeps
      printing CHECK, which is the fact, now documented.
- [x] F4 — no hard-coded counts left: probe over the four old values returns 0.
- [x] F5 — R9 first (65536 patterns, 0 mismatches, 254 NaN payloads excluded),
      then `tools/bf16.py` as the single conversion rule; `gguf_test` 101/0.
- [x] V — gguf_test 101/0, pyflakes clean, docs_claim green, session gate green,
      run_all 6/6. Two team-instrument bugs found on the way (self-reference in
      the conformance and evidence censuses) and fixed in the same round.
- [x] C — re-graded; see the round-13 re-review appended to
      `.subagents/critic-final/REVIEW.md`.

**Progress:**
- [x] T1 — `.subagents/` created: `README.md`, `TODO.md`, and `ORIGINAL.md` in all
      six member folders before their first run (each quotes the owner
      assignment verbatim and records the creation date and repo state).
- [x] T2 — `tools/codegraph_core.py`: 226 files, 61 `.md`, mtimes, 106+ internal
      edges, open checkboxes and source markers; stdlib only, no subprocess, no
      network, no git. Two instrument bugs found and fixed (self-scan of its own
      reports: markers 8 -> 19,220; doc-lag noise from identical checkout mtimes).
- [x] T3 — six members with `AGENTS.md`, `SKILL.md`, `codegraph.py` (own `SUB`,
      own focus, own extra check) and `reports/`; a runner with one retry; a
      structural gate with an in-gate negative control.
- [x] T4 — `.agents/skills/sub-agents/SKILL.md` (frontmatter valid, discovered via
      the `.claude/skills` symlink), based on the documented ADK patterns
      (sub_agents / AgentTool / Sequential / Parallel / Loop-with-critic).
- [x] T5 — `run_all.py`: 6/6 rc=0, first attempt each, receipts in
      `.subagents/*/reports/latest.{txt,json}`.
- [x] T6 — `check_subagents.py`: 20 checks, 0 failures; `--self-test` proves three
      independent detectors can fail (after fixing the control itself).
- [x] T7 — `critic-final/REVIEW.md`: **9/10 PASS** (threshold 7) with a
      per-criterion table; the one withheld point is the independence gap (no
      separate reviewer model is spawnable here — only the web-research agent),
      recorded as finding 1 rather than hidden.
- [x] T8 — records updated (this section, `errors.md` 6 entries, `user.md`
      directives 31-32, `.agents/README.md` index, `CHANGELOG.md` round 12);
      gates: `session_start_check` ok, `docs_claim_check` ok, pyflakes 4.1.0 clean
      on all nine new scripts, `py_compile` ok.

**Findings handed to the owner (proposals only, no code touched):** SV-1
(`AGENTS.md:66-67` pin without a source URL), SC-1 (`0xCBF43926` KAT missing from
`docs/FORMAT-V2.md`), TS-1 (`kotlin_stub_check.sh` in no workflow), CE-1
(`AGENTS.md:198/202/232` hard-coded counts vs. R21), CA-1 (`_decode_bf16`
implemented twice: `tools/gguf_reader.py:576`, `tools/safetensors_to_hydra.py:229`).
- [x] Session start: AGENTS.md + .agents/{rules,session,errors,user}.md read; 28 .md files listed; 2026 web research done (AGENTS.md budgets/dilution; enforcement-over-prose; Agent Skills spec) — findings recorded in R33 + errors.md + the ci-triage/repo-docs-audit skills.
- [x] R33 + gate 1j (tools/session_start_check.sh, wired into ci.yml after 1i; local run: ok, negative control proven).
- [x] `.agents/skills/`: 3 moved (session-workflow, engine-ci-verify, android-ndk-build) + 4 new (ci-triage, kotlin-stub-check, android-lint-gate, repo-docs-audit); `.claude/skills` = symlink.
- [x] session.md slimmed to current rounds (archive: .agents/docs/SESSION-ARCHIVE.md).
- [x] all-.md audit + fixes (28→33 files inventoried; 0 broken links; fixed: AGENTS.md §8 dead code-scanning.yml ref (rewritten to verified reality), FORMAT-V2 ↔ HYDRA2-RESEARCH cross-links, root README tree + CI-tier note + skill pointer, .agents/README index (skills table, R33, archive), android/README dual-engine reality (file tree, libs, run flow, tabs), CHANGELOG backfill (rounds 5/6/6-follow-up/7 were missing), RESEARCH-LOG §7 correction (event-triggered workflow could never run — deleted same day), session-workflow skill (R33 step + format template), android-ndk-build description (8 pitfalls), rules/README/AGENTS "32 rules" → 33)
- [x] errors/user docs (errors.md: R33 root-cause entry + the archive-split incident; user.md: directives 22–25)
- [x] PR #62 closed (superseded; factual comment records why: its CI red = the stage-2 API error fixed by merged PR #64)
- [x] commit + push + PR: **PR #65** (ec344a9). CI: **15 pass / 4 skipped / 0 fail** (run 40353536462 + 40353536695) — incl. the NEW gate 1j (session-start marker) green on CI, docs-claim green with the archive exclusion + negative control, Android lint green. Main-only tier jobs correctly skipped on the PR.

**Awaiting owner:** merge PR #65. Post-merge: main carries R33 + gate 1j; any session that skips the read protocol will turn the next push red.


## Round 2026-10-26 (round 8: full transformer attention (v4), .hydra2 sparse-MoE, Android sampler, CLAUDE.md fix — owner prompt)

**Session start (R33):** 2026-10-26 (branch `arena/fe34926d-bestai`, base main 3d13d5a = merged PR #65, all checks green). Read before touching code: AGENTS.md (full) → session.md (current round) → errors.md (top 3) → rules.md (R1–R33) → user.md (25 directives) → Environment.md (Arena section) → engine-ci-verify + ci-triage + repo-docs-audit SKILL.md → docs/FORMAT-V2.md (full), docs/FORMAT.md (v3 section), docs/ARCHITECTURE.md (full). PLUS the owner's directive for this round: read ALL .md files first — done (33 files, all folders; the 4 product specs, all 7 skills, all .agents files, both READMEs, CHANGELOG).

**Owner directives (2026-10-26 evening, verbatim intent):** "session.md kann bleiben" (do NOT optimize/rewrite session.md; it stays committed and readable by everyone — verify it is not git-ignored) + "habe ein prompt erstellen lassen" (the pasted Principal-Architect prompt is the work plan) + "lese alle dateien, alle .md dateien, als erstes, und dann bitte optimieren (außer session.md …)" + "weiter machen, suche auch im Web wenn nötig" + "Bitte intelligent" + "Finde Fehler und toten Code" + "lade über python weitere Linter und so herunter" + "KEINE Stubs oder Fake". No native todo tool exists in this environment — the plan below is the todo list (session.md precedent).

**Prompt audit, corrected against live main 3d13d5a (the prompt was written against a pre-round-4 state; R26 — verify before acting):**
- Claim "5 of 7 roadmap items checked; [ ] Full transformer forward pass, primitives NOT wired into an end-to-end layered forward pass" — **STALE.** Round 4 (merged via PR #57 → main) already shipped `hydra_engine_step_tf()`: per-layer ternary SwiGLU blocks + RMSNorm + RoPE + KV sink/append, format v3, tested (`test_tf_*`), roadmap item already `[x]`. What is genuinely missing for a FULL transformer: **attention** — no Q/K/V projections, no causal scaled dot-product attention.
- Claim ".hydra2 sparse-MoE: zero implementation" — **TRUE** (FORMAT-V2.md: "No part is implemented").
- Claim "hydra_jni.c does not expose hydra_sample_token / KV state to Android" — **TRUE** (HydraEngine.kt ignores sampling params; documented on the interface).
- Claim ".claude/skills symlink breaks on Windows; CLAUDE.md hidden in .agents/" — **TRUE** (web-verified 2026-10-26: Claude Code v2.1.277+ reads AGENTS.md only as a FALLBACK when no CLAUDE.md/.claude/CLAUDE.md/CLAUDE.local.md exists above the cwd; a committed symlink checks out as a one-line text file on `core.symlinks=false`; Claude's Edit/Write refuse symlinked paths; the import pattern `CLAUDE.md` containing `@AGENTS.md` is the cross-platform fix — sources recorded in RESEARCH-LOG §10).
- Invariant kept: the v1/v2 starter baseline `[471, 386, 385, 386, 385, 386, 385, 386]` (start_token=42) stays 100% intact — all engine work is ADDITIVE (new format versions / new functions), never a rewrite of the legacy path (user.md #11).

**Plan (milestones; order = dependency, each verified locally before the next — zero stubs, zero fakes):**
- [x] M-A: R33 session start — all 33 .md files read; round 8 section + marker; prompt audit corrected above.
- [x] M-B: session.md visibility — verified tracked (23 .agents files in git, `git check-ignore` clean); fix the STALE .gitignore comment (names the deleted `.agent_memory/` + top-level RESEARCH.md); add `.agent_memory/` as an ignore (local scratch only — repo memory lives in `.agents/` per owner decision).
- [x] M-C (prompt M4): real root `CLAUDE.md` (`@AGENTS.md` + `@.agents/CLAUDE.md`), docs updated (AGENTS.md §5 table, .agents/README.md, CHANGELOG); Windows symlink behaviour documented honestly.
- [x] M-D (owner: linters + bugs + dead code): pip-install additional linters (pylint, bandit, pyflakes for the Python tools; existing: cppcheck/clang-tidy/shellcheck/ESLint) → run everything → fix REAL findings; dead-code hunt (declared-but-never-called functions in C; unused imports/vars in Kotlin/JS/Python).
- [x] M-E (prompt M3): expose the C sampler (temperature / min-p / repetition penalty) through `hydra_jni.c` + `HydraBridge.kt` + `HydraEngine.kt`; default greedy calls 100% unchanged; kotlin stubs updated with the new `external fun`s; `kotlin_stub_check` + `compose_scroll_check` + `jni_signature_check` (CI javac) green.
- [x] M-F (prompt M1, corrected): FULL attention on top of v3 → **format version 4** (new version value, backward compatible: v1/v2/v3 files and the baseline stream untouched): per-layer Wq/Wk/Wv ternary planes + the existing Wg/Wu/w1/scale; `hydra_transformer_forward_step()` = pre-norm RMSNorm → ternary Q/K/V (NEON/AVX2/scalar dispatch) → RoPE → KV cache (sinks + window) → causal scaled dot-product attention (deterministic fixed-point) → residual → RMSNorm → SwiGLU FFN → residual → final RMSNorm → W_out logits; CLI + engine dispatch; tests incl. KV progression, RoPE position increment, min-p sampling, hand-computed case, NEON-vs-scalar same-build parity.
- [x] M-G (prompt M2): `.hydra2` sparse-MoE container per docs/FORMAT-V2.md — header parser + BOTH-ENDS validation (R14), top-k router (softmax over selected), expert streaming loader (pread, crc32 per read), fixture generator (make_model.py or gguf_to_hydra.py), tests (`test_hydra2_*` + security refusals + routing determinism).
- [x] M-H (prompt M5): roadmap checkboxes only after M-E/M-F/M-G are green (M6 invariant: 100% implemented + automated test); `tools/test_count_baseline.txt` updated in the same commit as the tests.
  - 2026-10-26: M-B..M-G deliverables each verified present in the tree before checking (M-B: .gitignore comment + `.agent_memory/` ignore; M-C: real root `CLAUDE.md`; M-D: linter runs + fixes from the previous round; M-E: `hydra_sample*` plumbing in `hydra_jni.c`; M-F: v4 loader/engine/tests + baseline stream re-verified; M-G: `src/hydra_v2_container.c` + 120-check `hydra2-test` (ASan/UBSan clean, gcc `-fanalyzer` clean on all three C files, fixture generator, CI wiring in `ci.yml` + `lint.yml`). Baseline file: x86 174->219, arm 183->228 with the dated entry (ARM re-measure on the CI leg). `docs/FORMAT-V2.md` updated: real implementation status, K/V wire format + 16-byte alignment recorded as `[CODE]` decisions.
- [x] M-I: .md optimization pass (all files EXCEPT session.md) — findings from the full read fixed in place; docs for the new versions/sampler/CLAUDE.md; CHANGELOG entry; Environment.md round-8 section (own section only).
  - 2026-10-26: all 33 .md files scanned for round-8 staleness. Fixed in place: `docs/FORMAT-V2.md` (implementation boundary, K/V wire format + 16-B alignment as dated `[CODE]` decisions), `docs/FORMAT.md` (new "Version 4" section: layout/forward pass/constraints/honest no-v4-writer status; the 4-GiB note no longer says "not yet implemented"), `docs/ARCHITECTURE.md` (new "Version 4 forward pass" section + components table), `README.md` (v4 feature line, Android sampler clause, the `.hydra2` roadmap item split into done-container [x] + open-inference [ ] with the spec-section evidence), `android/README.md` (the "ignores sampling params" claim is false since M-E: runInferenceSampled + fixed seed + temp-0 baseline), `CHANGELOG.md` (round-8 entry), `.agents/Environment.md` (round-8 section: pip linter installs + versions + full finding triage + recreate commands), `.agents/errors.md` (two real analyzer-found bugs + the regex-insertion process error). Files verified stale-free and left untouched: user.md, rules.md, the 7 skills, the .agents/docs/* research files (their "no v2 reader" statements are historical records of their own audit dates).
- [x] M-J: full gate sweep (AGENTS.md §3 order), commit, push, PR (facts only; owner merges).
  - 2026-10-26: gate sweep per AGENTS.md §3 order — every gate green or explicitly
    SKIP/blocked-out-loud (jni_signature: no javac, CI covers; ARM execution + NDK:
    no toolchain/SDK in sandbox, CI covers; mirror-test clang step: no clang driver,
    said out loud per R23). Full results in the commit message of 75b2649 and in the
    PR #67 description. Committed as 75b2649 (40 files, +5022/−212), pushed, PR #67
    opened (facts only). Merge: owner.

## Round 2026-10-26 (round 9: GGUF verification — spec conformance, the ggml_type bug, the pinned llama.cpp smoke, the behavior gate, the .hydra2 GGUF boundary, all-.md pass)
**Session start (R33):** 2026-10-26 (branch `arena/75337031-bestai`, base `0522d68` = merged PR #67). Read before the first edit: AGENTS.md, .agents/session.md (rounds 7-8), .agents/errors.md (top entries), .agents/rules.md (R2/R14/R23/R25/R26/R32/R33), .agents/user.md, .agents/Environment.md (round-8 section), docs/GGUF-IMPORT.md (full), docs/FORMAT-V2.md (header + boundary), README.md (Features + Android + tools tree), CHANGELOG.md (round-8 entry), tools/gguf_test.py + gguf_reader.py + gguf_to_hydra.py (current state), Makefile (gguf-test target) + .github/workflows/ci.yml (test-run), and - for the smoke test - the pinned llama.cpp source in /tmp/lc (llama-arch.cpp, llama-vocab.cpp, llama-graph.cpp, models/llama.cpp, llama-model.cpp, ggml.h enum) plus the official sources fetched fresh (ggml-org/ggml include/ggml.h + docs/gguf.md).


**Owner directive (verbatim intent):** "super, habe schon gemerged, dann prüfe nochmal, ob man dann GGUF dings modelle dort nutzen kann etc, also dass diese wirklich richtig schreiben, mit ihrer ganzen Intelligenz etc!!! mache tests, schaue im Web, und mache dann Doku etc!!!! alles an .md dateien aktualisieren!" — PR #67 merged by the owner as `0522d68` before this round started.

**Question answered (honestly):** the app is dual-engine. The **llama.cpp
engine** (submodule pinned at v0.5.0, `7fe450e19305b828c199d602c23a8337aaa1f03b`,
`LlamaEngine.kt` + `llama_jni.cpp`, `isExperimental = false` per
LlamaEngine.kt) is the main engine and runs GGUF with full transformer
inference — that is the "ganze Intelligenz" path. The `GGUF → .hydra`
converter is a documented 64-dim projection (seed model, not the source
network); its output now has a behavior gate that states exactly what it
can and cannot prove.

**Plan + status (all local-gated before commit):**
- [x] R9-A: web verification against official sources — ggml_type enum
      (ggml-org/ggml `include/ggml.h`) and the GGUF spec (ggml-org/ggml
      `docs/gguf.md`; the ggml-org/gguf repo does not exist).
- [x] R9-B: bug found by the enum audit — `tools/gguf_reader.py`
      quantised-name table wrong (31=TQ1_0/32=TQ2_0/34=MXFP4 vs official
      34=TQ1_0/35=TQ2_0/39=MXFP4, +40/41/42 missing, 31–33/36–38 reserved).
      Fixed; converter refusal now names tensor + layout
      (`token_embd.weight (TQ1_0)`); regression gate `run_type_names` in
      `tools/gguf_test.py` (6 current names + 6 reserved slots + message).
- [x] R9-C: spec conformance checked (header order, 13 KV types, tensor
      info, offsets relative to data section, alignment; version 2–3).
      LE-only = spec-conformant (spec: assume LE, not detectable);
      64-byte name cap not enforced (harmless) — both documented.
- [x] R9-D: behavior gate `run_behavior` (converted model: two identical
      `./hydra-run` runs + ≥2 distinct tokens, not the input repeated,
      for (0,24)/(3,40)/(11,16)); measured streams before choosing the
      threshold (token 0 → 3 distinct, tokens 3/11 → 2 distinct; ≥3 would
      have failed on the real 4-token fixture — 16-token scratch fixture
      gave 8–9 and does not count).
- [x] R9-E: pinned llama.cpp smoke — built the pin (codeload tarball,
      `cmake -B build -DCMAKE_BUILD_TYPE=Release -DLLAMA_CURL=OFF`,
      `--target llama-cli llama-server`); `tools/gguf_minimal_llama.py`
      (NEW, stdlib, fixed-seed LCG, 2 layers / dim 64 / heads 4 / ffn 192,
      99-token BPE charmap, empty merges, 21 tensors) → `llama-cli -m
      /tmp/smoke.gguf -p "a" -c 64 -n 4 -t 1 --temp 0` on the pin:
      **prompt 36 082.5 t/s, generation 5 640.6 t/s, generated text
      `1'aV+uE~`** (random by construction, byte-identical across
      runs, `llama-cli -p "a" -c 64 -n 8 -t 1 --temp 0`). Generator
      fixes from the run + the Qodo review (R9-I):
      `tokenizer.ggml.model`="gpt2" (not "BPE" — "unknown tokenizer"),
      `token_type` INT32 with the pinned enum (chars NORMAL=1,
      specials CONTROL=3 — the original file had them REVERSED, which
      is why the first smoke printed nothing),
      `tokenizer.ggml.add_bos_token` / `padding_token_id` (not the
      `llama.*` names — those are parsed but ignored by the pin),
      `output_norm.weight`, `llama.feed_forward_length`, LCG weights
      with real signs, ffn layout `{n_embd,n_ff}` / `{n_ff,n_embd}` in
      this build. F16 variant reaches a ggml type mismatch in the pin
      (f32 act × f16 norm in `ggml_mul`) → `--dtype f32` default
      (library + gate + docs aligned). `run_minimal_llama` keeps the
      generator alive in CI (dtype, token types, keys). llama-cli in
      this build is always-REPL: closed stdin → `> ` prompt
      busy-loop (sandbox artifact, documented).
- [x] R9-F: `.hydra2` boundary — `src/hydra_v2_container.c` refuses the
      GGUF magic BY NAME (bytes 0x47 0x47 0x55 0x46, LE u32
      0x46554747; points at LlamaEngine + converter +
      docs); +2 checks in `tests/test_hydra2_container.c` (suite 120→122;
      `tools/test_count_baseline.txt` M-G note updated in this commit).
- [x] R9-G: ALL .md updated — GGUF-IMPORT.md §11 + §4/§9, README
      (dual-engine, import bullet, tools tree, 122), FORMAT-V2.md
      (GGUF not a v2 container), CHANGELOG (round-9 entry + 122),
      errors.md (round-9 mistakes), Environment.md (round-9: /tmp reset,
      venv /tmp/lintenv2, llama.cpp build recipe), this section.
- [x] R9-H: gate sweep + commit + push + PR #68 (facts only; owner
      merges). Local results: gguf_test green incl. the three new
      gates; hydra2-test 122/0; flawfinder 0; cppcheck 0; make 0
      warnings; bandit medium+ 0 (20 Low = triaged asserts/subprocess,
      lint.yml comment); pyflakes clean; v1 baseline `471 386 385 386
      385 386 385 386` unchanged; llama.cpp build + smoke as above.
- [x] R9-I: Qodo code-review fixes on PR #68 (all 11 findings; every
      one verified against the sources before acting — all were
      valid): (1) **HIGH**: the R33 session-start marker (top of this
      section) was missing — `tools/session_start_check.sh` would
      have been RED in CI; (2) the two tokenizer keys renamed to the
      `tokenizer.ggml.*` namespace the pin actually reads
      (llama-arch.cpp L394/397 — the `llama.*` names are parsed but
      ignored); (3) README: llama.cpp availability per ABI (arm64
      selectable / x86_64 packaged but not selectable / armeabi-v7a
      absent — MainActivity.kt L84-94 + CMakeLists verified); (4)
      `run_behavior` now asserts the exact requested token count;
      (5) token types NORMAL(1)/CONTROL(3) — the original file had
      them reversed (UNKNOWN chars are dropped by the BPE
      detokenizer: the root cause of the first empty smoke output);
      (6) dtype defaults aligned on f32 (library, gate, docs);
      (7) §11.4 intro now describes the fixture as F32; (8) LCG
      produces real (-1,1) weights (was [0, 2·scale)); (9) GGUF
      magic written as bytes 0x47 0x47 0x55 0x46 / LE u32 0x46554747
      (the C message had the BE value 0x47475546) — C, FORMAT-V2,
      CHANGELOG; (10) generator docstring: stale numbers replaced by
      a pointer to §11.4, fact count corrected; (11) the §11.4
      recipe runs the generator from the repo root (it lived in a
      post-`cd` directory that does not contain tools/). Smoke
      re-run after the fixes: prompt 36 082.5 t/s, generation
      5 640.6 t/s, text `1'aV+uE~` (deterministic). NOT implemented
      (owner call, per the standing "CI speed up safely" directive):
      a CI job that builds the pin and runs the smoke automatically —
      Qodo's optional suggestion, 10–15 min per PR. The manual
      recipe is documented in §11.4; re-run it whenever the pin
      changes.

## Round 2026-10-26 (round 10: the documented smoke recipe bug, all-.md English pass, real-model verification, the opt-in real-model gate)

**Session start (R33):** 2026-10-26 (branch `arena/75337031-bestai`, base `634a4fb`). Read before the first edit: AGENTS.md, .agents/session.md (rounds 8-9 + R9-I addendum), .agents/errors.md (top entries), .agents/rules.md (R2/R14/R23/R25/R26/R32/R33), .agents/user.md (directive list), .agents/Environment.md (round-9 section), docs/GGUF-IMPORT.md (full, esp. 11.4 recipe), README.md (GGUF + Android bullets, tools tree), CHANGELOG.md (round 9), docs/FORMAT-V2.md, the GitHub issue the owner linked (the `timeout` recipe bug, GGUF-IMPORT.md 458-460), and — for the English pass — every *.md in the repo (systematic scan, 33 files) plus .github/workflows/{lint,release,ci}.yml and the Makefile; for the real-model work: tools/gguf_test.py (main/run_behavior/run_v3), tools/gguf_to_hydra.py (dim/vocab handling), tools/gguf_reader.py (is_decodable/decode_rows), android/app/src/main/java/dev/hydrastone/{LlamaBridge,LlamaEngine}.kt + android/app/src/main/cpp/llama_jni.cpp (the load path).

**Owner directive (verbatim intent):** "prüfe folgendes [the Qodo issue: the documented smoke command makes `timeout` treat `OMP_NUM_THREADS=1` as an executable], und prüfe CI und alles auf englisch dort übersetzen, dann alle .md dateien analysieren und bearbeiten, prüfe die tests, lade dir wirklich ein Modell herunter, was evtl so 300 MB ist und was schreiben kann, und finetune alles, ermögliche alles auf der app."

- [x] R10-A: recipe bug fixed + verified — the §11.4 line was
      `(sleep 10 | timeout 10 OMP_NUM_THREADS=1 $LLAMA/…/llama-cli …)`:
      `timeout` takes `OMP_NUM_THREADS=1` as the command to run, so the
      documented recipe NEVER launched llama-cli (reproduced:
      `timeout: failed to run command 'OMP_NUM_THREADS=1'`). Now
      `timeout 10 env OMP_NUM_THREADS=1 …`; the fixed recipe was
      executed verbatim from a clean cwd and printed the fixture
      output (`1'aV+uE~`, prompt 34 410.1 t/s, generation 6 323.4 t/s).
      errors.md entry added.
- [x] R10-B: all .md + CI in English. Systematic scan (word-boundary
      regex, umlauts + strict German function words; the first scan
      was a false-positive disaster — "commit" contains "mit").
      Translated: .github/workflows/lint.yml (6 blocks), release.yml
      (15 blocks), Makefile (1 line), .agents/docs/SESSION-ARCHIVE.md
      (rounds 3-6 + doc-audit section, ~90 lines of German prose).
      Kept deliberately: verbatim owner directives quoted in
      user.md/session.md/errors.md (they record what the owner said),
      the MIT licence string, and the v1 product's German CLI output
      (product identity, quoted by the docs; string-format gates).
      YAML re-validated; the C/Kotlin runtime strings stay German
      (documented scope decision).
- [x] R10-C: real model downloaded + verified. The sandbox network
      allows only github.com/codeload/api.github.com/npm/pypi — Hugging
      Face, raw.githubusercontent.com and the GitHub LFS endpoint are
      all unreachable, and GitHub stores model files >= 100 MB via
      LFS, so the "300 MB" target is not deliverable here (proven for
      gemma-3-270m-it-Q8_0 291.5 MB, qwen2.5-0.5b-instruct-q4_k_m,
      smollm2-135m — every copy found was an LFS pointer, 133/134 B).
      The largest real writing model obtainable: **llama-68m-chat-v1
      Q8_0, 73 018 688 B (73.0 MB)**, arch llama, 2 layers, dim 768,
      ctx 2048, 32k vocab, 21 tensors (16 Q8_0 + 5 F32), from
      BodhiSearch/BodhiApp (HF-cache layout, plain git blob) via the
      codeload tarball. Run on the PINNED llama-cli v0.5.0 (open
      stdin): "The capital of France is" -> "...France.<|im_end|>",
      prompt 109.4 t/s, generation 6.6 t/s (2 threads); longer prompt
      greedy 172.7 / 4.4 t/s; temp 0.7 generation 8.2 t/s. Honest
      ceiling: a 68M model writes thin prose; the pipeline (load,
      tokenize, full decode incl. Q8_0, sampling, detokenize, stream)
      is what is proven.
- [x] R10-D: the app path. LlamaBridge.load(path, nCtx) -> JNI ->
      `llama_model_load_from_file` (pinned v0.5.0) -> generate/
      cancel/unload: a thin wrapper, no size/arch/quant restriction of
      our own, architecture delegated to the pinned loader (the
      README claim, now backed by a real model). The model's ctx
      2048 fits the app clamp 256..8192. NOT measured (R32): the
      .so inside the APK on a device/emulator — the Android CI tier
      compiles the exact JNI source; the x86_64 emulator is the
      documented device-side path.
- [x] R10-E: the opt-in real-model gate. `tools/gguf_test.py
      --real-model <path>` (6 checks, off by default so CI stays
      offline + fast): magic bytes 47 47 55 46, full parse, every
      decodable tensor decodes, the converter projects it to .hydra
      v3 (dim 64, 2 layers, vocab 1024, 30 976 tokens dropped), the C
      engine runs the projection deterministically (two runs
      byte-identical, 16 tokens, non-degenerate). llama-68m: 107
      checks, 0 failed; the default set stays 101.
- [x] R10-F: docs — GGUF-IMPORT.md 11.7 (the full section: source,
      recipe, numbers, what each tool proved, what is not measured,
      the size ceiling + how a normal machine runs a ~300 MB model
      through the identical commands), README (GGUF bullet + tools
      tree), CHANGELOG round 10, Environment.md (model location +
      re-fetch recipe), user.md (directive 29). Gate sweep green,
      commit + push (PR #68 updated).


## Round 2026-10-26 (round 11: post-merge audit completion — JNI sampler config tests, web-console sampler, Android v2 header diagnostics, tf_row_dot SIMD)

**Session start (R33):** 2026-10-26 (branch `arena/476154f4-bestai`, base `fd1848a` = merge of PR #68). Read before the first edit: AGENTS.md (full), .agents/session.md (rounds 6-10), .agents/errors.md (top entries), .agents/user.md (directive list, tail), .agents/Environment.md (ARM/toolchain section: APT block, zig compile-only path, no qemu), .gitignore (safety check: .agents/ fully tracked, 23 files, owner-decision comment — NOT touched), the root inventory (no HYDRA2-RESEARCH.md at root — it lives at .agents/docs/HYDRA2-RESEARCH.md; no docs/HYDRA2.md — v2 format docs are docs/FORMAT-V2.md), the Makefile (full: targets, AVX2 probe, jni-batch-test deps), .github/workflows/ci.yml (jni-signatures job: jni_signature_check runs for BOTH bridges; android_header_check job), android/app/src/main/cpp/hydra_jni.c (full: 5 JNI exports, runInferenceSampled validation inline), android/app/src/main/cpp/hydra_batch.h (the single-source header pattern), tests/test_jni_batch.c (structure + includes), tools/jni_signature_check.sh (parameterised, negative-control via args), tools/android_header_check.sh (full check list), android/app/src/main/java/dev/hydrastone/MainActivity.kt (analyseHydraFile + describeMagic), android/app/src/main/res/values/strings.xml (err_magic_*), server.js (/api/infer handler, runInference, constants), public/app.js (run flow: POST /api/infer sends {path,prompt,steps,request_id} only), public/index.html (opt-* settings block), tools/server_test.js (structure, node:test), tools/hydra_train.js (deterministic hill climbing — no sampling), src/hydra_engine.c (M2 sampler, v3 step_tf, v4 hydra_transformer_forward_step, tf_row_dot scalar core, sampler step), src/hydra_simd.h + src/hydra_neon.h (existing AVX2/NEON kernels: accumulate_agg + v2 plane unpack), src/hydra_v2_container.c (open/magic, route_top_k, tensor types) + include/hydra_v2_container.h (HYDRA2_MAGIC_STR "HYDRA2\0\0", public API) + include/hydra_model.h (sampler ctx), android/app/build.gradle + android/CMakeLists.txt (hydra_v2_container.c is HOST-ONLY, not in the app build), tests/test_engine.c (M-E sampler suite, sampled-loop section, AVX2/NEON parity test patterns), tools/test_count_baseline.txt (x86 219 / arm 228, hydra2 122 separate).

**Owner directive (verbatim intent):** the post-merge audit from the owner: update test_jni_batch.c to also test the new JNI sampler configuration; the JNI signature gate should strictly cross-check all native methods across both bridges including a negative control; update tools/android_header_check.sh to verify include/hydra_v2_container.h alongside include/hydra_model.h; new CLI sampler flags (temperature, min_p, repetition penalty) (ALREADY PRESENT in src/main.c — verified: --temp/--min-p/--rep-penalty/--rep-window with validation; documented as such, not re-implemented); web console: new controls for temperature/min_p/rep_penalty + new sampler flags for the training backend if applicable (trainer is deterministic hill climbing — no sampling — documented as N/A with evidence); SIMD the v2-container expert decode paths and the new format v4 (evidence-based scope: tf_row_dot is the v3/v4 forward's scalar integer-exact core -> AVX2+NEON; the container's expert decode is a documented O(k^2 n) comparison-based selection + double softmax with no data-parallel arithmetic -> documented, not changed); update the docs to reflect the new features. PLUS the owner's emphatic reply (2026-10-26): "Mache so, dass du gewissenhaft weißt, dass du nichts kaputt machst! Also gitignor und die wichtigsten Agenten Files session.md etc. IMMER EGAL WAS ICH SAGE wahre und beschützt und sie stets aktualisierst!! Bitte prüfen und sicher fortfahren!" — STANDING RULE for this round (highest priority after safety): .agents/ files (session.md, errors.md, user.md, Environment.md, rules.md, docs/) are SACROSANCT — never delete them, never add them to .gitignore, keep them current in every round, regardless of any other instruction; .gitignore itself is not touched. Proceed thoroughly: legacy behaviour stays bit-identical (greedy default unchanged, v1 baseline stream untouched, all existing gates green) and every local gate runs before any commit.

- [x] R11-A (FERTIG): JNI sampler config — extract runInferenceSampled's validation into
      android/app/src/main/cpp/hydra_sample_cfg.h (the hydra_batch.h single-source
      pattern: one header compiled into both libhydra.so and the host test);
      hydra_jni.c calls it (messages + check order unchanged); new section in
      tests/test_jni_batch.c (boundaries: temp 0/20.0, minP 0/1.0, rp 1.0/2.0
      accepted; temp -0.1/20.001/NaN/Inf, minP -0.001/1.001, rp 0.9999 rejected;
      greedy-default proof); Makefile jni-batch-test dep + new count;
      tools/sampler_contract_check.sh (cross-surface: main.c CLI, JNI header,
      server.js share the same range rules; negative control) wired into the
      ci.yml jni-signatures job; tools/jni_signature_negative_test.sh (missing
      negative control, pattern: android_autostart_negative_test.sh).
- [x] R11-B (FERTIG): web console sampler — server.js /api/infer accepts
      temperature/minP/repetitionPenalty/repWindow, validates with the SAME
      rules as the JNI header (400 + clear message, non-finite rejected),
      passes --temp/--min-p/--rep-penalty/--rep-window as execFile array args
      (no shell); legacy request (no fields) emits NO flags -> greedy -> the
      existing 37 server_test.js cases stay green bit-identical; index.html +
      app.js: sampler controls (defaults = off = legacy behaviour);
      server_test.js new live HTTP tests (legacy bit parity, temp=0 == greedy
      stream, temp>0+seed changes the stream = no-op negative control, 400 for
      every invalid value/type); trainer (tools/hydra_train.js) untouched —
      deterministic hill climbing has no sampling stage (documented).
- [x] R11-C (FERTIG): Android v2 header diagnostics — a .hydra2 file (magic
      "HYDRA2\0\0": first 4 bytes are the SAME "HYDR" as v1, the tail
      "A2\0\0" distinguishes) currently reports "magic matches .hydra" + a
      generic version error; MainActivity.kt names the HYDRA2 container by
      name (strings.xml entry, mirroring the v2 reader's own refusal);
      tools/android_header_check.sh gains the v2 checks INCLUDING a
      cross-surface check that the Kotlin constant equals bytes 4-7 of
      HYDRA2_MAGIC_STR in include/hydra_v2_container.h (the v2 header path
      verified alongside the v1 header path, as audited).
- [x] R11-D (FERTIG): SIMD — tf_row_dot (the 2-bit ternary x int8 dot that v3 step_tf
      and v4 hydra_transformer_forward_step call ~384x/token) gets
      hydra_avx2_tf_row_dot (src/hydra_simd.h, 128-bit: zero-padded 16-byte
      load + pshufb unpack x4 + maddubs + int32 sum — INTEGER EXACT, so the
      pinned streams stay valid) and hydra_neon_tf_row_dot (src/hydra_neon.h,
      vtbl1 + vmlsabdq); dispatch in hydra_engine.c (AVX2 runtime probe as in
      M3, NEON compile-time as in the load path); parity tests in
      tests/test_engine.c (x86: LCG-random rows/vectors over dims 4..64 +
      all-code sweep + extremes vs an independent scalar reference, the M3
      pattern; NEON: same, compiled-only locally per Environment.md (no qemu),
      executed on the ARM CI leg); tools/test_count_baseline.txt x86/arm lines
      updated in the SAME commit (R21). Container SIMD: NOT done, with the
      evidence (route_top_k is comparison-based selection + double softmax,
      the container has no data-parallel arithmetic, plane unpack is already
      AVX2/NEON); float ops (rmsnorm/rope/swiglu/attention) stay scalar
      (bit-exact pinned streams).
- [x] R11-E (FERTIG): docs — AGENTS.md (v3/v4 transformer + per-layer KV, .hydra2
      container, sampler on all surfaces, SIMD map, the two new gates),
      README.md (CLI sampler flags if not already documented), CHANGELOG.md
      round 11, errors.md (as they happen), user.md directive 30.
- [x] R11-F (FERTIG): gates + PR — the full 5-part local gate (make clean && make &&
      make test && make test-run; static analysis; python; node; guardrails),
      v1 baseline stream [471 386 385 386 385 386 385 386] unchanged,
      docs_claim_check, test_count_check vs the new baseline, zig aarch64
      compile check of the NEON path (Environment.md's recorded substitute),
      then commit on arena/476154f4-bestai, push, PR with facts only, CI green
      including the ARM leg.

### R11 results (measured, 2026-10-26)

- **R11-A:** `hydra_sample_cfg.h` (single source: ranges temp 0..20 / minP
  0..1 / rp >= 1.0 / window 0..4096, isfinite, order temp→minP→rp, codes
  0–3, defaults 0/0/1.0/64). jni-batch-test **109 checks, 0 failed** (was
  86). `sampler_contract_check.sh` **34/34 GRÜN** + negative control rc=1
  (drift "C header '25.0' vs server.js '20'"). `jni_signature_negative_test.sh`
  local SKIP rc=0 (no javac in sandbox — said so), S1 phantomMethod /
  S2 load-Arität / sed-Guard; CI proof on JDK 17. Both wired into the
  ci.yml jni-signatures job; `workflow_yaml_check.sh` green (5 workflows).
- **R11-B:** server.js strict validation (`typeof v !== 'number' ||
  !Number.isFinite(v)`, window additionally integer); field-less request
  appends NO flags (legacy bit-exact). ECHTER BUG gefangen vom eigenen
  Test: `Number(null) === 0` ließ NaN-serialisiertes Feld als temp 0
  durch — jetzt 400. server_test **43/43** (was 37). `hydra_train.js`
  unangetastet (deterministisch, dokumentiert).
- **R11-C:** MainActivity.kt `HYDRA2_TAIL_U32 = 0x00003241L` +
  HeaderRule("format", …) + `err_magic_hydra2` (strings.xml).
  android_header_check **28/28 GRÜN** (was 21) inkl. 2 computed
  cross-surface pins (python3 rechnet die Kotlin-Konstanten aus den C
  Magic-Strings) + Negativ rc=1 (0x00009999L). R_gen.kt-Stub →
  kotlin_stub_check OK 0 errors.
- **R11-D:** AVX2- + NEON-Kernel für `tf_row_dot` (Design: 1 Row-Byte =
  4× 2-Bit-Codes ⇒ 8-dim-Chunk = 2 Row-Bytes + 8 x-Bytes; T3={0,1,-1,0};
  integer-exakt, Lane-Bound 2·127, Total-Bound 64·127=8128 ⇒
  bit-identische Streams, kein Re-Pinning). Parity:
  `/tmp/par_check.c` (recreatable: gcc -O2 -mavx2 -Iinclude,
  scalar-Referenz + LCG, dims 4..64 × 2000, x exakt dim groß) **ALL OK**
  + **ASan-CLEAN** (x exakt dim groß). `hydra-test` **225/225 x86**
  (was 219; +6 AVX2-Parity-Checks); ARM-Baseline 228 → **234** (progn.
  +6 NEON-Checks, CI-ARM-Leg misst). Pinned v3/v4-Streams gültig (die
  beiden Stream-Tests haben die erste Kernel-Version gefangen). NEON:
  zig-aarch64-Full-Compile (engine + tests) rc=0, kein lokaler ARM-Run
  (kein QEMU — Environment.md-Rezept; CI neon-test = Ausführungsbeweis).
- **R11-E:** AGENTS.md §2.1 (v3/v4 + SIMD-Dispatch + dokumentierte
  Scope-Entscheidungen Container-Top-k/Floats), §3 (jni 109, server 43,
  beide neuen Gates), README (CLI-Sampler-Flags + Contract),
  CHANGELOG R11, docs/FORMAT-V2.md (SIMD-Status-Punkt).
- **R11-F:** 5-Teil-Gate lokal GRÜN (alle Suites, Linter — inkl.
  cppcheck 2.13.2 aus Quell-Build, exakter CI-Befehl, 0 Warnungen;
  Python, Node, alle Guardrails, actionlint, session-check). v1-Legacy:
  die [471 386 …]-Referenz ist ein Session-Log-Wert eines alten Modells
  und KEIN Code-Pin (grep belegt: nur in session.md); der relevante
  Proof ist die Bit-Identität gegen den Base-Commit-Build — gemessen:
  v1-Stream (normal UND --fast, 32 Tokens) byte-identisch Base vs.
  Branch. Commits e157480 + 5142045 (NULL-Checks, CI-cppcheck-2.13
  nullPointerOutOfMemory) + 6b0797a (row[16]={0}, CI-cppcheck-2.13
  uninitvar False-Positive, mit 2.13.2-Quellbuild reproduziert und
  danach rc=0). PR #70 geöffnet (FACTS ONLY). CI auf dem PR: **16
  passed / 0 failed**; 4 Jobs (neon-test QEMU, build-test, Android
  APK, GPU bench) by design skipping im PR — Owner-Regel: PR = Fast-
  Lint, main = voller Build. Der NEON-Runtime-Beweis (test_neon_
  tf_row_dot, 234er-Baseline) läuft nach dem Merge auf main.
  /tmp-Resets in dieser Runde: zvenv + lintenv neu aufgebaut
  (Rezepte Environment.md); pyyaml via pip --break-system-packages;
  llama.cpp-Submodule per `git submodule update --init` auf den Pin
  ausgecheckt (sonst pin-check "working tree"-Meldung).

## Round 2026-10-29 (round 12: the `.subagents` team — 3 web-research + 3 critic agents, per-agent skill + codegraph, graded review)

**Session start (R33):** 2026-10-29 (branch `freebuff/6daeacda62104e261f2b28ce`, base `94f8e08` = merge of PR #70). Read before the first edit: AGENTS.md (full) -> .agents/session.md (rounds 6-11 incl. the R11 results block) -> .agents/errors.md (top entries: the `timeout`/`env` recipe bug, the LFS dead ends) -> .agents/rules.md (R1-R33, §8 conflict order) -> .agents/user.md (30 dated directives) -> .agents/skills/session-workflow/SKILL.md + .agents/skills/repo-docs-audit/SKILL.md -> tools/session_start_check.sh (gate 1j: the marker must be in the LAST `## Round` section) -> tools/docs_claim_check.sh (its audited FILES array, incl. `.agents/skills/*/SKILL.md`) -> .github/workflows/{ci,lint,vibeworks-check}.yml (pyflakes/bandit scope, `git ls-files '*.py'` in vibeworks) -> .gitignore (NOT touched) -> `.claude/skills` (symlink to `../.agents/skills`). Web research before designing: Google ADK sub-agent patterns (adk.dev/workflows/patterns/, adk.dev/agents/workflow-agents/{sequential,parallel,loop}-agents/, adk.dev/sessions/state/, adk.dev/tools-custom/function-tools/) — findings recorded in the new `sub-agents` skill.

**Owner directive (verbatim intent, German):** "starte bitte 6 Agenten ... 3 die im Websuchen koennen und 3 die kritisieren muessen ... unsre Subs muessen in einem Ordner zusammen arbeiten der .subagents heisst! bevor jeder Anfaengt muss eine Original.MD erstellt werden ... fuer den Erstellst du einen Skill und eine eigene Agents.md ... fuer dich ein Skill namens 'Sub-Agents' ... IMMER Todo Liste nutzen?!! Am Ende IMMER einen criticer starten der deine Arbeit kritisieren muss ... Criticer soll auch in den andren Sub Agents schauen ... jeder soll ein py Script haben im eigenen Ordner der Codegraph nutzt ... NIEMALS FAKE NIEMALS STUBS ... keine Subs duerfen Code Aenderungen machen nur Vorschlagen ... KEIN RATEN". Artefacts stay English (R31), the conversation stays German.

**Plan (this is the todo list for the round; updated after every step — R2):**
- [x] T1 Create `.subagents/` with `README.md`, `TODO.md` (the reusable pipeline checklist) and `ORIGINAL.md` per sub-agent (created BEFORE its first run).
- [x] T2 One real shared code-graph engine (`.subagents/tools/codegraph_core.py`): all files, mtimes, every `.md`, include/import edges, TODO markers, open checkboxes ("what still needs changing").
- [x] T3 Six sub-agent folders, each with `AGENTS.md` (contract), `SKILL.md` (Agent Skills format, R29/R30), `codegraph.py` (own focus profile + own extra check) and `reports/`.
- [x] T4 `.agents/skills/sub-agents/SKILL.md` — the parent skill, based on the documented Google ADK patterns (sub_agents / AgentTool / Parallel / Loop-with-critic).
- [x] T5 Run every `codegraph.py` for real, capture the outputs as evidence, and store the receipts in each `reports/`.
- [x] T6 `.subagents/tools/check_subagents.py` — structural gate + in-gate negative control (R25), then run it.
- [x] T7 Final critic (`critic-final`) reviews the parent work AND the other five sub folders, scores 1-10; below 7 means rework until the findings are closed.
- [x] T8 Docs: user.md directive, `.agents/README.md` index pointer, CHANGELOG, this section; gates green (session-start, docs-claim, py_compile/pyflakes).

**Progress:**

## Round 2026-10-29 (round 13: closing the five team findings — pin source, CRC known answer, unwired Kotlin gate, hard-coded counts, duplicated bf16 decoder)

**Session start (R33):** 2026-10-29 (branch `freebuff/6daeacda62104e261f2b28ce`, base `94f8e08` + the uncommitted round-12 work). Read before the first edit: AGENTS.md (§2.2 the llama pin box, §3 the gate list, the `jni-batch-test` / `sampler_contract_check` / `server_test` / `contrast_check` lines), .agents/session.md (round 12 + its findings), .agents/errors.md (round-12 entries), .agents/rules.md (R5-R12, R21, R25, R26, R31, R32), .agents/user.md (directives 31-32), all six `.subagents/*/PROPOSALS.md` (the five findings), `docs/FORMAT-V2.md` (CRC rows 290/322 and rules 389-392), `tools/gguf_reader.py` + `tools/safetensors_to_hydra.py` (both `_decode_bf16` bodies and their call sites), `tools/gguf_test.py` (`run_safetensors` gate, line 661), `tools/llama_pin_check.sh` (`PIN_TAG`/`PIN_COMMIT`, lines 23-24), `.github/workflows/{ci,lint}.yml` (Gradle `assembleDebug` at ci.yml:739 and lint.yml:548).

**Plan (todo list for the round):**
- [x] F1 (SV-1) `AGENTS.md`: cite the primary source next to the llama.cpp pin instead of leaving it a bare claim.
- [x] F2 (SC-1) `docs/FORMAT-V2.md`: document the CRC-32 known-answer values the C API already pins, so a third-party writer can self-check.
- [x] F3 (TS-1) `AGENTS.md` §3: close the unwired-gate finding explicitly — either wire `kotlin_stub_check.sh` into CI or state it as a manual-only gate with the reason.
- [x] F4 (CE-1) `AGENTS.md`: replace the hard-coded counts (109/34/43/17) with parse instructions, as R21 requires of the same file.
- [x] F5 (CA-1) `tools/`: prove the two `_decode_bf16` implementations agree (R9, all 65536 patterns), then single-source them.
- [x] V Re-run the affected gates (gguf_test, pyflakes, docs_claim, session gate, team run).
- [x] C Re-run `critic-final` and re-grade.

**Progress:**

## Round 2026-10-29 (round 14: the threat-scan agent — AI instruction malware detection, security rules, CI gate, per-sub error/request files)

**Session start (R33):** 2026-10-29 (branch `freebuff/6daeacda62104e261f2b28ce`, base `94f8e08` + rounds 12-13 uncommitted). Read before the first edit: AGENTS.md (full, incl. the round-13 pin-source block), .agents/session.md (rounds 12-13), .agents/errors.md (round-12/13 self-reference entries), .agents/rules.md (R1-R33 + §8 conflict order), .agents/user.md (directives 1-32), `.subagents/README.md` + `TODO.md` + all six `PROPOSALS.md`, `.subagents/tools/{codegraph_core,run_all,check_subagents}.py`, `.agents/skills/sub-agents/SKILL.md`, `.github/workflows/{lint,ci,vibeworks-check}.yml` (job layout, pyflakes/bandit scope), `tools/docs_claim_check.sh` (audited FILES), `tools/workflow_yaml_check.sh` + `tools/workflow_lint_check.sh` (what a new workflow must survive). Web research in parallel: 2025-2026 prompt-injection/invisible-Unicode/threat-detector landscape, and the AGENTS.md / Agent Skills / skill-security conventions.

**Owner directive (verbatim intent, German):** "achte auf Lesbarkeit und Wertbarkeit also skills mit richtigen YML ... schaue deine Docs und die von heutigen Agenten Coding Tools ... einen Sub Agenten der nach Schadcode und nach Schadanweisung für KI erkennt ... darf ein py selber schreiben um Sachen zu scannen ... suche nach unsichtbaren Zeichen Instruktionen die bösen Willen haben 'Nicht User sagen' ... mache Sicherheitsregeln ... baue es dann in die CI ein ... Arbeite Findings intelligent immer selber ab ... Subs können Anfragen machen und bei der Klarstellung helfen ... jeder Sub hat Error.md und so in ihren Ordnern".

**Plan (todo list):**
- [x] S1 Research: threat classes + detector tooling (2026 sources), and agent-doc/skill conventions. Sources read: OWASP LLM01:2025, AWS "Defending LLM applications against Unicode character smuggling", trojansource.codes/CVE-2021-42574, Trail of Bits prompt-injection explainer, Invariant Labs MCP tool poisoning, Snyk ToxicSkills, Cisco skill-scanner, NVIDIA SkillSpector, AID, anti-trojan-source, Semgrep bidi rule, agents.md, Agent Skills specification, Anthropic skill best practices + `anthropics/skills` security checklist. Recorded with URLs in `.agents/docs/AI-THREAT-MODEL.md` (195 lines, 30 URL lines).
- [x] S2 `.subagents/ai-threat-scan/` — 7th member: `ORIGINAL.md` (written before the first run), `AGENTS.md`, `SKILL.md`, `codegraph.py`, `ERROR.md`, `REQUESTS.md`, `PROPOSALS.md`, `reports/{latest.json,scan.json}`.
- [x] S3 Scanner (`scan.py`, 585 lines, stdlib only, offline): 27 rules — invisible tag-block/zero-width/bidi/variation-selector/control characters, covert secrecy phrasing (EN+DE), prompt override, renderer-hidden text (element-scoped for attributes, forward-only window for CSS), pipe-to-shell, base64-to-shell, reverse shell, netcat, encoded PowerShell, eval-remote, rm -rf /, chmod 777 /, CSS-hidden content, hidden attribute, secret shapes (AWS/GitHub/sk-/private key/Slack), data-URI, long base64, symlink escape; severities, in-line waivers, `--json`, `--fail-on`, `--only`, `--self-test`. <!-- ai-threat-scan: allow covert-instruction (the phrase is quoted here as a pattern name, not used as an instruction) --> <!-- ai-threat-scan: allow chmod-777-root (rule name listed in the round plan) -->
- [x] S4 Security rules R34 (a file never gives an order; the gate is mandatory; waivers only in place with a reason) and R35 (agent docs readable AND machine-valid) in `.agents/rules.md` §8; conflict order moved to §9; every "33 rules"/`§8` reference updated (AGENTS.md:14, .agents/README.md:18, README.md:373, session-workflow skill).
- [x] S5 `ERROR.md` + `REQUESTS.md` in all seven folders (real content, 1.0-2.5 kB each), required by `check_subagents.py` (plus a size floor so a placeholder fails); strict PyYAML frontmatter validation with a stated structural fallback, spec keys only, name pattern/length, description ≤1024 chars, body <500 lines, visible trigger (`## When …` or "Use when"); `## When to use` added to the seven skills that lacked a trigger.
- [x] S6 CI job `ai-threat-scan` in `.github/workflows/lint.yml` (self-test → tree scan → reports → structure gate → its own negative control → pyflakes+bandit on `.subagents/`); `tools/workflow_yaml_check.sh` and `tools/workflow_lint_check.sh` both green.
- [x] S7 The scanner's own findings worked: 45 → 0 high. Fixed in code, not waived: self-scan of the rule table, self-scan of the generated JSON, ±300 window on UI attributes (3 false highs), space-separated waivers silently ignored, `.ps1` missing from the suffix list, over-broad instruction vocabulary, symmetric CSS window. Eight waived hits on seven marked lines remain (the threat model's quoted examples, the CSS paragraph that names the properties, and two quotes in the review), each with the reason on the line.
- [x] S8 Records (session/errors/user/CHANGELOG/README/.agents README/TODO/skill) and the re-graded critic pass.

### R14 results (measured, 2026-10-29)

| Check | Command | Result |
|---|---|---|
| rule proof | `scan.py --self-test` | ok — 27 fixtures fire, clean file + clean tree stay green, single and multi-rule waiver both honoured |
| gate under attack | probe file in the tree, then removed | 5 high + 1 medium, exit 1, tag payload decoded (`IGNORE`); after removal exit 0 |
| tree scan | `scan.py .` | 0 high, 0 medium, 21 low, 8 waived hits on 7 marked lines, over 232 text files (24 binary skipped) |
| structure gate | `check_subagents.py` | 7 folders, 24 checks, 0 failures (strict PyYAML) |
| gate control | `check_subagents.py --self-test` | ok — 7 deliberate defects, one per file, each rejected by its own detector |
| team run | `run_all.py` | 7/7 members rc=0 on the first attempt, reports written |
| workflows | `workflow_yaml_check.sh`, `workflow_lint_check.sh` | ok (5 files parsed / 4 linted, negative controls proven) |
| python | `pyflakes .subagents/`, `bandit -r .subagents -s B610` | clean; B610 triaged as Django's `QuerySet.extra()` vs. the shared `extra=` keyword (comment in the job) |
| protocol | `session_start_check.sh`, `docs_claim_check.sh` | ok / all banned claims absent |

**Progress:**
- Built the 7th member (`ai-threat-scan`) with a 27-rule stdlib scanner, worked its own 45 findings down to 0 high in code, added R34/R35, the threat model with sources, `ERROR.md`+`REQUESTS.md` in all seven folders (gate-enforced), strict Agent Skills YAML validation, and the CI job `ai-threat-scan`. End-to-end control: a probe file in the real tree gave 5 high + 1 medium, exit 1, decoded payload; after removal exit 0. `critic-final`: **9/10 PASS** (the withheld point is that no runner has executed the new job yet; this round does not push).

## Round 2026-10-29 (round 15: close the self-scan blind spot, resolve the two paths, re-prove the gate)

**Session start (R33):** 2026-10-29 (branch `freebuff/6daeacda62104e261f2b28ce`, base `94f8e08` + rounds 12-14 uncommitted). Read before the first edit: `AGENTS.md` (protocol + §2.3 Python pipeline + §3 gate list), `.agents/rules.md` (R1-R35, §8/§9), `.agents/session.md` (rounds 13-14 + the R14 results table), `.agents/errors.md` (round-14 entries), `.agents/user.md` (directive 33), `.subagents/ai-threat-scan/{scan.py,AGENTS.md,SKILL.md,ERROR.md,REQUESTS.md,PROPOSALS.md,ORIGINAL.md}`, `.subagents/tools/{check_subagents.py,run_all.py}`, `.subagents/README.md`, `.subagents/critic-final/REVIEW.md`, `.agents/docs/AI-THREAT-MODEL.md`, `.github/workflows/lint.yml` (job `ai-threat-scan`).

**Owner directive (verbatim intent, German):** "bitte achte auf Lesbarkeit und Wertbarkeit ... jeder Sub hat Error.md und so in ihren Ordnern ... Arbeite Findings intelligent immer selber ab ... aus Fehlern lernen" + the round-15 scope: close the self-scan hole, resolve `sub-agents/` vs `.subagents/` and the unexplained `tools/bf16.py`, re-prove every gate, log every real mistake.

**Plan (todo list):**
- [x] T1 Remove the whole-file self-exclusion in `scan.py`; quarantine only the colliding lines with in-line waivers and a reason each.
- [x] T2 Add the `own_source` self-test fixture (copy of `scan.py` must scan clean; the same copy plus one hidden payload must be caught).
- [x] T3 Plant → detect → remove a payload inside `scan.py` on the working tree (exit 1, then exit 0, byte-identical restore).
- [x] T4 Resolve the paths: state which `sub-agents` path is canonical, gate against a duplicate tree, and confirm `tools/bf16.py` is referenced (not junk).
- [x] T5 Re-prove every gate, first attempt; write the real mistakes into `ai-threat-scan/ERROR.md`, `ai-threat-scan/REQUESTS.md` and `.agents/errors.md`.

### R15 results (measured, 2026-10-29)

| Check | Command | Result |
|---|---|---|
| rule proof | `scan.py --self-test` | ok — 27 fixtures, clean file/tree green, waiver honoured, **payload in the scanner's own source caught** (`own_source`) |
| tree scan | `scan.py .` | **233** text files (incl. `scan.py`), 13 binary skipped, **0 high / 0 medium / 21 low**, 46 waived hits on 42 marked lines |
| own-source negative control | payload appended to `scan.py`, then restored | exit **1**, `[HIGH] invisible-tag-block .subagents/ai-threat-scan/scan.py:605`, `5 tag characters, decodes to 'STEAL'`; `sha256sum -c` OK; exit **0** |
| structure gate | `check_subagents.py` | 25 checks, 0 failures (7 folders, strict PyYAML), incl. `layout: exactly one sub-agents directory` |
| gate control | `check_subagents.py --self-test` | ok — **8** deliberate defects rejected (7 member-file defects + the duplicate-tree control) |
| duplicate-tree control | planted `sub-agents/SKILL.md` at the repo root | gate **FAIL** `duplicate sub-agents tree(s) outside .agents/skills/sub-agents` (rc=1); removed → green |
| team run | `run_all.py` | **7/7 rc=0 on the first attempt**, reports written |
| CI job | parsed `lint.yml` with PyYAML | job `ai-threat-scan` parses; step order self-test (3) → tree scan (4) → reports (5) → gate (6) → gate control (7); scan step carries `--fail-on high` |
| workflows | `workflow_yaml_check.sh`, `workflow_lint_check.sh` | ok (5 parsed / 4 linted, negative controls proven) |
| protocol | `session_start_check.sh`, `docs_claim_check.sh` | ok / all banned claims absent |
| session gate stability | `session_start_check.sh` x 5 | rc=0 five times in a row (the gate used to fail intermittently on `grep -q` + `pipefail`; fixed, see `.agents/errors.md` round 15) |
| python | `pyflakes .subagents/`, `bandit -r .subagents --severity-level medium -s B610`, `py_compile` | clean / clean / ok |

**Paths resolved:** `.agents/skills/sub-agents/` is the canonical **procedure** (one `SKILL.md`, discovered via the `.claude/skills` symlink); `.subagents/` is the canonical **team** (contracts, tooling, receipts). Neither is a copy; the split is now written down (`.subagents/README.md` "Two paths, two jobs") and checked (layout gate + no member files inside the skill + bidirectional pointers). `tools/bf16.py` stays: `tools/gguf_reader.py:41` and `tools/safetensors_to_hydra.py:82` both `import bf16`, and it is documented in `README.md:358` and `AGENTS.md` §2.3.

**Progress:** done — every gate green on the first attempt; nothing committed (delivery not authorized).

## Round 2026-10-29 (round 16: waivers that cannot become a blind spot)

**Session start (R33):** 2026-10-29 (branch `freebuff/6daeacda62104e261f2b28ce`, base `94f8e08` + rounds 12-15 uncommitted). Read before the first edit: `AGENTS.md` (protocol, §1 rules table, §3 gates), `.agents/rules.md` (R21, R25, R34), `.agents/session.md` (round 15 + its R15 results table), `.agents/errors.md` (round-15 entries), `.subagents/ai-threat-scan/{scan.py,AGENTS.md,SKILL.md,REQUESTS.md,ERROR.md,PROPOSALS.md}`, `.agents/docs/AI-THREAT-MODEL.md` (§3 detector, §4 blind spots), `.subagents/tools/{check_subagents.py,run_all.py}`, `.github/workflows/lint.yml` (job `ai-threat-scan`).

**Owner directive (verbatim intent, German):** "Arbeite Findings intelligent immer selber ab ... aus Fehlern lernen ... jeder Sub hat Error.md ... Englisch alles" + the round-16 scope: a waiver may only hide the finding it names, never an unrelated one, and never without a reason.

**Plan (todo list):**
- [x] W1 Strict waiver grammar in `scan.py`: a waiver suppresses only when it names that exact rule id and carries a reason of meaningful length; unknown ids, missing/short/placeholder reasons suppress nothing.
- [x] W2 Non-suppressing waivers surface as `waiver-invalid` **low**, and the underlying finding stays. Decision changed mid-round from "high" to "low": the payload is already reported at its own severity, so escalating the diagnostic would double-count one defect; the note adds the reason the marker did nothing. It cannot be waived (appended directly, never through `_add`).
- [x] W3 Waiver inventory in the report and the JSON: file:line, rule, and the reason that justified each suppression.
- [x] W4 `--self-test` fixtures `waiver_valid`, `waiver_other_rule`, `waiver_no_reason`, `waiver_placeholder`, multi-rule; each fails loudly on regression.
- [x] W5 Real-tree proof: payload in `scan.py` under a mismatched waiver, then under an unreasoned one → exit 1; byte-identical restore (`sha256sum -c`) → exit 0.
- [x] W6 Docs (`AGENTS.md`, threat model), `REQUESTS.md` R-6 closed honestly, records + full gate re-run.

**Results (all observed, first attempt unless noted):**

| Gate | Command | Observed |
|---|---|---|
| scanner self-test | `scan.py --self-test` | `SELF-TEST ok`, rc=0 (27 rule fixtures, clean file/tree, 6 waiver fixtures, own source) |
| tree scan | `scan.py . --fail-on high` | 233 text files, **0 high / 0 medium / 21 low / 46 waived on 42 lines**, `VERDICT: PASS`, rc=0 |
| waiver inventory | `--json` parse | 46 entries, all with a reason, shortest reason 24 chars; 38 entries in `scan.py` on 36 lines |
| mutation: reasons ignored | copy of `scan.py`, reason check forced true | `SELF-TEST FAIL` rc=2, 4 failures (no-reason and placeholder cases) |
| mutation: ids widened | copy of `scan.py`, ids widened to every rule | `SELF-TEST FAIL` rc=2 (`waiver_other_rule`) |
| plant A, mismatched id | tag payload plus a waiver naming another rule, inside `scan.py` | rc=1, `[HIGH] invisible-tag-block scan.py:716`, decoded payload printed; `sha256sum -c` OK after restore, rc=0 |
| plant B, no reason | tag payload plus the correct id and no reason, inside `scan.py` | rc=1, high finding **plus** `[LOW] waiver-invalid scan.py:716`; rc=0 after restore |
| plant C, ordinary file | `docs/waiver-probe.md` carrying a copied waiver for another rule | rc=1 naming `docs/waiver-probe.md:3`; removed, rc=0 |
| structure gate | `check_subagents.py`, `--self-test` | 25 checks 0 errors / 8 defects rejected |
| team run | `run_all.py` | 7/7 member rc=0 |
| workflow | PyYAML parse + order assert | `ai-threat-scan` parses, self-test step before the tree scan |
| session/docs | `session_start_check.sh`, `docs_claim_check.sh` | ok / no forbidden claims |
| python | `pyflakes`, `bandit`, `py_compile` | clean / clean / ok |

**Progress:** done — the waiver rule is implemented, documented and proven on the real tree; every gate green on the first attempt after the fixes recorded in `.agents/errors.md` and `.subagents/ai-threat-scan/ERROR.md`. Nothing committed, nothing pushed.

## Round 2026-10-29 (round 17: coverage audit — three hidden-instruction classes were not detected)

**Session start (R33):** 2026-10-29 (branch `freebuff/6daeacda62104e261f2b28ce`, base `94f8e08` + rounds 12-16 uncommitted). Read before the first edit: `AGENTS.md`, `.agents/rules.md` (R21/R25/R34), `.agents/session.md` (round 16 results), `.agents/errors.md`, `.subagents/ai-threat-scan/{scan.py,AGENTS.md,codegraph.py,REQUESTS.md,ERROR.md,PROPOSALS.md}`, `.agents/docs/AI-THREAT-MODEL.md`, `.github/workflows/lint.yml`.

**Owner directive (intent, German):** close the hidden/encoded instruction gaps the mission names, decide from evidence, prove every detector, no fake and no stub, learn from mistakes, English artefacts.

**Audit before coding (measured, not assumed).** Existing detectors in `scan.py`: tag block, zero-width/`Cf`, bidi controls, variation selectors, raw controls, `covert-instruction`, `prompt-override`, `hidden-html`, `hidden-with-instructions`, `html-hidden-attr`, `css-hidden-content`, shell/secret/encoded shapes. Gaps found by reading the rule table against the mission's class list: **no detector decodes anything** (base64/hex/percent/ROT13 that *becomes* an instruction is invisible today), **no detector handles look-alike letters** (Cyrillic/Greek homoglyphs spelling an instruction), **no detector reports private-use-area characters**. Two existing rules also had no self-test fixture at all (`pipe-to-shell`, `symlink-escape`) - the self-test only asked "did some rule fire somewhere", never "does every rule have a fixture".

**Plan (todo list):**
- [x] C1 Coverage matrix (class -> rule id + fixture / NOT covered) into `.subagents/ai-threat-scan/AGENTS.md`, with the NOT-covered rows as backlog.
- [x] C2 `encoded-instruction` (high): base64/hex/percent/ROT13 candidates are decoded and the result must match instruction language; near-miss encodings must stay clean.
- [x] C3 `homoglyph-instruction` (high): Cyrillic/Greek look-alikes de-confused; fires only when de-confusing *creates* an instruction match (documented FP limit: bare mixed-script tokens are not flagged - this tree has 25 legitimate Greek math tokens).
- [x] C4 `private-use-character` (low): PUA ranges reported as informational (0 occurrences in the tree today, so no noise; 23 binary files are skipped anyway).
- [x] C5 Self-test: one fixture per detection rule asserted mechanically (`fixture_rules == detection_rules`, counts equal), per-fixture `path` + `line` assertion, near-miss negatives, plus fixtures for the two rules that had none.
- [x] C6 Mutation control per new detector on a copy: weakened copy must make `--self-test` exit non-zero.
- [x] C7 Real-tree probes (one file per new class), `scan.py .` exit 1 naming each probe with its rule id, delete, byte-identical baseline (`sha256sum -c`), exit 0, same file count.
- [x] C8 `codegraph.py` rule-drift set extended, docs (AGENTS.md matrix, threat model), records, full gate.

**Results (all observed; first attempt unless the row says otherwise):**

| Gate | Command | Observed |
|---|---|---|
| scanner self-test | `scan.py --self-test` | `SELF-TEST ok`, rc=0: **30 detection rules, one fixture each with path+line assertion, 6 near misses clean**, waiver grammar, own source |
| tree scan | `scan.py . --fail-on high` | 233 text files, **0 high / 0 medium / 21 low / 48 waived on 44 lines** (40 in `scan.py` on 38), `VERDICT: PASS`, rc=0 |
| rule drift | `ai-threat-scan/codegraph.py` | `declared 31`, `missing metadata: none`, `declared but never used: none`, `verdict: PASS` |
| mutation: decoding off | copy of `scan.py`, decoder loop emptied | `SELF-TEST FAIL` rc=2 (`encoded_b64/hex/pct.md` did not fire) |
| mutation: de-confusion off | copy of `scan.py`, `if False` | `SELF-TEST FAIL` rc=2 (`homoglyph.md`) |
| mutation: PUA off | copy of `scan.py`, `elif False` | `SELF-TEST FAIL` rc=2 (`pua.md`) |
| probe plant, high rules | 3 probe files in `docs/`, `scan.py . --fail-on high` | rc=1: `[HIGH] encoded-instruction docs/_scan_probe_encoded.txt:1`, `[HIGH] homoglyph-instruction docs/_scan_probe_homoglyph.txt:1` |
| probe plant, low rule | same tree, `--fail-on low` | rc=1 and also `[LOW] private-use-character docs/_scan_probe_private_use.txt:1` |
| probe cleanup | delete 3 files, `sha256sum -c /tmp/baseline.sha256` | rc=0, **242/242 `OK`**, scan rc=0, 233 text files (same as before the plant), 0 probe paths left |
| structure gate | `check_subagents.py` / `--self-test` | 25 checks 0 failures, rc=0 / 8 defects rejected, rc=0 |
| team run | `run_all.py` | 7/7 `rc=0`, first attempt each |
| workflow | `workflow_yaml_check.sh`, `workflow_lint_check.sh` | 5 files parsed / 4 linted, negative controls proven |
| session/docs | `session_start_check.sh`, `docs_claim_check.sh` | ok / no banned claims |
| python | `pyflakes`, `bandit`, `py_compile` | rc=0 / rc=0 (0 issues) / rc=0 |
| CI job | PyYAML parse + order assert | `ai-threat-scan` parses, 10 steps, `--self-test` at step 4 **before** tree scan at step 5 |

**Progress:** done — three missing classes detected and proven end to end, the self-test now forces a fixture per rule, the coverage matrix and its backlog are written down. Nothing committed, nothing pushed.

## Round 2026-10-29 (round 18: nested encodings and comment-form instructions)

**Session start (R33):** 2026-10-29 (branch `freebuff/6daeacda62104e261f2b28ce`, rounds 12-17 uncommitted). Re-read before editing: `AGENTS.md`, `.agents/rules.md`, `.agents/session.md` (round 17), `.agents/errors.md`, `.subagents/ai-threat-scan/{scan.py,AGENTS.md,codegraph.py,ERROR.md,PROPOSALS.md,REQUESTS.md}`, `.agents/docs/AI-THREAT-MODEL.md`, `.github/workflows/lint.yml`.

**Re-verification of the previous round's claims (STEP 0, observed):** `--self-test` ok with **30 detection rules**; tree scan **233 text files, 0 high / 0 medium / 21 low / 48 waived**, rc=0; `rules_table()` has **31 entries (30 detection + `waiver-invalid`)**; `AGENTS.md` carries the coverage matrix with a `NOT covered` table. Every claim from the previous round holds - no correction entry needed.

**Plan before edit (rows chosen, rows refused):**

- [x] N1 **Close: nested / multi-layer encodings.** Decode iteratively, `MAX_DECODE_DEPTH = 3`, with a decoded-length cap and a `seen` set for loop detection, so `base64(rot13(instruction))` is found. **Rule id stays `encoded-instruction`**: same class, same severity, same fixture family; the provenance is recorded in the finding detail as the chain (`base64->rot13, depth 2`). A second id would split the waiver/fixture story for no detection benefit - stated here as the justification.
- [x] N2 **Close: instruction in a visible code comment.** New rule `comment-instruction`, severity **low**, narrow form only: a comment body that *addresses* an agent (`AI:`, `agents:`, `assistant:`, `model:`, `note to the AI:`) **and** then carries an action verb. Measured before coding: the broad shape (any agent word + any imperative in a comment) hits **54 legitimate lines** in this tree (README bullets, `server.js` route docs, `CHANGELOG` prose) - rejected as noise; the narrow addressed form hits **0**. FP limit accepted: an addressed comment without an action verb is not reported, and a plain imperative comment (`# run this before merging`) is not reported at all - the channel is visible to a human reader, so this stays informational.
- [x] N3 **Refuse, keep as backlog with a concrete next step:** (b) full UTS #39 confusable coverage (needs the data file + a size budget) and (c) payloads in binary/image/PDF files (needs an extraction job). Both stay in the matrix as NOT-covered; the report already prints the binary skip count, so the residual risk is stated rather than hidden.
- [x] N4 Self-test: one positive fixture per new/changed class asserting rule id + line, near-miss negatives (nested-but-harmless encodings, quoted/negated trigger wording, a plain imperative comment), fixture-set equality with the rule table preserved.
- [x] N5 Mutation controls on copies: depth forced to 1 (nested fixture must fail), comment matcher neutered (comment fixture must fail).
- [x] N6 Real tree: baseline manifest, one probe per newly covered class, `scan.py .` exit 1 naming each probe with its rule id, delete, `sha256sum -c`, exit 0, same file count.
- [x] N7 Docs (`AGENTS.md` matrix delta + backlog rows, threat model rules/sources), records, full gate in one pass.

**Results (all observed, one pass unless a row says otherwise):**

| Gate | Command | Observed |
|---|---|---|
| scanner self-test | `scan.py --self-test` | `SELF-TEST ok`, rc=0: **31 detection rules, one fixture each with rule id + line 1, 10 near misses clean**, waiver grammar, own source |
| tree scan | `scan.py . --fail-on high` | 233 text files, **0 high / 0 medium / 21 low / 48 waived on 44 lines** (40 in `scan.py` on 38), `VERDICT: PASS`, rc=0 |
| nested proof | temp file with `base64(rot13(phrase))` | rc=1, `[HIGH] encoded-instruction probe.md:1`, detail `base64->rot13 payload decodes to instruction text at depth 2: '<the decoded instruction phrase>'` |
| mutation: depth → 1 | copy of `scan.py`, `range(1, 2)` | `SELF-TEST FAIL` rc=2: `rule encoded-instruction did not fire on nested_encoded.md` |
| mutation: comment check off | copy of `scan.py`, `if False:` | `SELF-TEST FAIL` rc=2: `rule comment-instruction did not fire on comment_ai.py` |
| probe plant (high) | 2 probes in `docs/`, `scan.py . --fail-on high` | rc=1: `[HIGH] encoded-instruction docs/_scan_probe_nested.txt:1` (+ depth detail), `[LOW] comment-instruction docs/_scan_probe_comment.txt:1` |
| probe plant (low) | same tree, `--fail-on low` | rc=1, both probes named with their rule ids |
| probe cleanup | delete 2 probes, `sha256sum -c /tmp/base18.sha256` | rc=0, **242/242 `OK`**, 0 probe paths left, scan rc=0, 233 text files (pre-plant count) |
| rule drift | `ai-threat-scan/codegraph.py` | declared 32, missing metadata none, declared-but-unused **none**, `verdict: PASS` |
| structure gate | `check_subagents.py` / `--self-test` | 25 checks 0 failures / 8 defects rejected, both rc=0 |
| team run | `run_all.py` | 7/7 `rc=0`, first attempt each |
| workflow | `workflow_yaml_check.sh`, `workflow_lint_check.sh` | 5 parsed / 4 linted, negative controls proven |
| session/docs | `session_start_check.sh`, `docs_claim_check.sh` | ok / no banned claims |
| python | `pyflakes`, `bandit`, `py_compile` | rc=0 / rc=0 (0 issues) / rc=0 |
| CI job | PyYAML parse + order assert | `ai-threat-scan` parses, 10 steps, `--self-test` step 4 **before** tree scan step 5 - no workflow change needed, the new invariants are asserted inside `--self-test` |

**Progress:** done — nested encodings (depth 3) and addressed comment instructions are detected and proven; two design mistakes found and fixed with fixtures; backlog reduced to the rows that genuinely need a decision. Nothing committed, nothing pushed.

**Post-round verification (owner request: fetch + check whether the docs are right):**

- `cloud_git fetch` ran: `main -> FETCH_HEAD`, remote head `4b9e075` (2026-11-09),
  local `94f8e08` (2026-10-27) - **0 commits ahead locally, 48 behind**, 18 paths
  uncommitted (rounds 12-18), `.gitignore` untouched. No merge/rebase performed:
  resolving that divergence needs the owner.
- Doc audit against the code: `rules_table()` = 32 (31 detection + `waiver-invalid`),
  every detection rule appears in the `AGENTS.md` matrix, threat model / PROPOSALS /
  gate row all say 31. Two stale claims found and fixed: `.agents/README.md`
  ("six-agent team") and `.subagents/README.md` ("27 detection rules"). Both recorded
  in `.agents/errors.md` and this folder's `ERROR.md`.
- Re-ran the gate after the doc edits: tree 233 files, 0 high / 0 medium / 21 low /
  48 waived, rc=0; self-test 31 rules / 10 near misses, rc=0; `check_subagents.py`
  25 checks 0 failures + 8 defects rejected; `run_all.py` 7/7 rc=0; workflow YAML 5
  parsed / lint 4, negative controls proven; session/docs checks ok; `pyflakes`,
  `bandit` (0 issues) and `py_compile` rc=0 after reinstalling the tools into
  `/tmp/qa` (the sandbox had dropped them; the first run reported rc=1 because the
  module was missing - that is a reinstalled tool, not a code change).

## Round 2026-11-27 (round 19: remote divergence analysis — how bad is it?)

**Session start (R33):** 2026-11-27 (branch `freebuff/6daeacda62104e261f2b28ce`, 18 paths uncommitted from rounds 12-18). Read: `AGENTS.md`, `.agents/rules.md`, `.agents/user.md`, `.agents/session.md` (round 18), `.agents/errors.md` (top 3). Owner request: analyse what the 48 fetched remote commits changed and how severe the collision with the uncommitted work is. Analysis only - no merge, no checkout (R17/R20).

**Plan (before measuring):** compare `HEAD` with `FETCH_HEAD` per path, classify every dirty path as *colliding* or *free*, and measure the real conflict size with `git merge-file` on temporary copies (the worktree is not touched) instead of guessing from `git status`.

**Observed:**

| Question | Measurement |
|---|---|
| Remote head / local head | `4b9e075` (2026-11-09, merge of PR #87) vs `94f8e08` (2026-10-27); **0 ahead, 48 behind** |
| Commit-level merge | `HEAD` is an ancestor of `FETCH_HEAD`; `git merge-tree` rc=0 - a fast-forward is possible, no commit conflicts |
| Remote changes in our paths | 12 files under `.agents`/`.github` (2639+/689-); `.subagents/` **0 files**, `.agents/docs/AI-THREAT-MODEL.md` **0**, `tools/bf16.py` **0**, `git grep -i "ai-threat\|subagents"` on `FETCH_HEAD` **empty** |
| Remote `lint.yml` | 10 jobs, **no `ai-threat-scan`**; its 10 changed lines only add `src/hydra_moe.c` / `tests/test_hydra_moe.c` to gcc/clang/clang-tidy/asan |
| Our `lint.yml` | 11 jobs (the 10 plus `ai-threat-scan`, 10 steps); 3-way merge conflict count **0** - the job survives |
| Dirty vs remote-changed | 18 dirty, 57 remote-changed, **10 overlap**; none of the 10 is textually identical to the remote version |
| Real conflict size (`git merge-file --diff3`, temp copies) | **9 hunks in 6 files**: `AGENTS.md` 3, `.agents/README.md` 2, `.agents/errors.md` 1, `.agents/session.md` 1, `.agents/user.md` 1, `CHANGELOG.md` 1 |
| Auto-merge, no conflict | `.github/workflows/lint.yml`, `README.md`, `docs/FORMAT-V2.md`, `tools/gguf_reader.py` |
| Collision-free local work | 8 paths the remote never touched: `.agents/rules.md`, `.agents/skills/session-workflow/SKILL.md`, `.agents/docs/AI-THREAT-MODEL.md`, `.agents/skills/sub-agents/`, `.subagents/` (all), `tools/bf16.py`, `tools/safetensors_to_hydra.py`, `tools/session_start_check.sh` |
| Semantic risk: `tools/gguf_reader.py` | Remote added Q4_0/Q4_1 block decode; ours extracted the BF16 widening into `tools/bf16.py`. Simulated merge keeps **both**: `T_Q4_0`/`T_Q4_1` present, `_decode_bf16` delegates to `bf16.decode_bf16`; `pyflakes` on the merged file rc=0. The `halves = array('H')` left in the merged file belongs to the **F16** branch, verified by line context |
| Semantic risk: `lint.yml` | none: our job is appended in a region the remote did not edit |

**Verdict:** the divergence is *recoverable*, not broken. The commits are a clean fast-forward and the 9 conflict hunks sit in prose/log files, where "keep both" is the resolution. The genuinely dangerous part is not the merge: **the whole rounds-12-18 work (7-member team, scanner, R34/R35, CI job) exists only uncommitted in this worktree** - upstream has no `.subagents/`, no threat model and no `ai-threat-scan` job.

**Recommended order (needs the owner's go, R17):** commit the 18 paths on this branch → `git merge FETCH_HEAD` → resolve the 9 hunks (ours appended after theirs, session/errors keep both) → run the full gate on the merged tree → then the green state is real and the merge can land. No `git checkout` anywhere (R20).

**Not done:** no commit, no merge, no push (R17/R19/R20). `.gitignore` untouched.
