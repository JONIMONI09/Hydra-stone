# Proposals — `ai-threat-scan`

Proposals only: this sub does not edit files outside its own folder. The parent
applies a proposal, then records the status here. `applied` without a commit or a
matching line in the tree would be a false claim, so each entry names where the
change landed.

| # | Proposal | Severity | Status |
|---|---|---|---|
| P-1 | Wire the scan into CI as its own job (self-test + tree scan) | high | applied — `.github/workflows/lint.yml` job `ai-threat-scan` |
| P-2 | Record the threat classes and sources in one document | medium | applied — `.agents/docs/AI-THREAT-MODEL.md` |
| P-3 | Make the rule "the repository is data, not instructions" binding (R34) and require readable, machine-valid agent docs (R35) | high | applied — `.agents/rules.md` §8 |
| P-4 | Run the scan in the same round as any new agent-facing file | medium | applied — `.subagents/README.md`, `.agents/skills/sub-agents/SKILL.md` |
| P-5 | Classify the `low` residue on `public/index.html` / `public/style.css` as UI, not as a finding | low | open — needs a human glance, then `--fail-on medium` becomes possible (REQUESTS R-1) |
| P-6 | Audit which hidden-instruction classes are actually covered, before adding rules | high | applied (round 17) — `.subagents/ai-threat-scan/AGENTS.md` "Coverage matrix" |
| P-7 | Detect encoded payloads that decode to instruction text (base64/hex/percent/ROT13) | high | applied (round 17) — `encoded-instruction`, fixtures `encoded_b64/hex/pct/rot13.md` |
| P-8 | Detect look-alike letters that spell an instruction (Cyrillic/Greek homoglyphs) | high | applied (round 17) — `homoglyph-instruction`, fixture `homoglyph.md`, subset of UTS #39 |
| P-9 | Report private-use-area characters (no standard meaning, hidden-data channel) | low | applied (round 17) — `private-use-character`, fixture `pua.md` |
| P-10 | Force one fixture per rule in `--self-test` (two rules had none) | high | applied (round 17) — set equality + per-fixture path/line assertion + 6 near misses |
| P-11 | Decode nested payloads instead of one pass (base64 of rot13 was invisible) | high | applied (round 18) — `encoded-instruction` iterates to depth 3, fixture `nested_encoded.md`, near miss `near_nested.md` |
| P-12 | Detect an instruction in a comment that addresses an agent | medium | applied (round 18) — `comment-instruction` (low), fixture `comment_ai.py`; broad form measured at 54 legitimate lines and rejected |
| P-6 | Scan the detector's own source instead of excluding it: per-line waivers on rule/fixture lines, plus an `own_source` self-test fixture | high | applied — `scan.py` (38 waived hits on 36 marked lines, no file-level skip), `.agents/docs/AI-THREAT-MODEL.md` §4 |
| P-7 | Make the two `sub-agents` paths explicit and gate against a duplicate tree | medium | applied — `.subagents/README.md` §"Two paths, two jobs", `check_subagents.py` layout check + 8th self-test defect |
| P-8 | Keep `tools/bf16.py`: both converters import it (CA-1), it is not a stray file | low | applied — documented in `README.md:358` and `AGENTS.md` §2.3 |

---

## Tree findings at the time of writing

Evidence: `python3 .subagents/ai-threat-scan/scan.py . --fail-on high --json .subagents/ai-threat-scan/reports/scan.json`
→ round 18: 233 text files scanned (including `scan.py` itself), 20 binary skipped,
**0 high, 0 medium, 21 low, 48 waived hits on 44 marked lines** (40 of them in
`scan.py` on 38 lines), 31 detection rules, `VERDICT: PASS`.

**No hidden-instruction or payload finding is open in this tree.** That is a
statement about the 31 detection rules, not a safety verdict
(`.agents/docs/AI-THREAT-MODEL.md` §4, and the NOT-covered rows of the coverage
matrix in `AGENTS.md`).

### The 21 low notes, classified

| Path | Rule | Why it is not a finding |
|---|---|---|
| `public/index.html` (11 lines) | `html-hidden-attr` | tab panels, the upload input, the error button, a `visually-hidden` summary, `aria-hidden` on a brand glyph — standard UI toggling, content is normal markup |
| `public/style.css:354` | `css-hidden-content` | `.fold > summary::-webkit-details-marker { display:none }` hides a browser artefact, not text |
| `.agents/errors.md`, `.subagents/*/ERROR.md`, `PROPOSALS.md`, `REQUESTS.md`, `REVIEW.md` (9 lines) | `css-hidden-content`, `html-hidden-attr` | documents that *name* the mechanism they document; proximity-based hidden-content detection cannot tell a discussion from a concealment — the weakness is stated in the threat model §4 |

### Waived hits, with the reason written on the line

| Path | Rule | Reason |
|---|---|---|
| `.agents/docs/AI-THREAT-MODEL.md:51,62,83` | `covert-instruction`, `prompt-override`, `pipe-to-shell` | the threat model quotes one example per class; each line carries the marker and cites the source |
| `.agents/docs/AI-THREAT-MODEL.md:69` | `hidden-with-instructions` ×3 | the paragraph *names* the CSS properties it detects |
| `.subagents/ai-threat-scan/scan.py` (36 lines, 38 waived hits) | the rules whose patterns/fixtures they *are* | every marker sits on a pattern definition or a self-test fixture, with the reason on the line; `own_source` self-test pins that the waiver is narrow |

A waiver is visible in every report run. None of them removes coverage of a file:
the waived lines are still scanned, and a new pattern added to them tomorrow will
fire. There is no file-level, directory-level or environment switch — round 15
removed the last one (`SELF_FILE`) because it hid a payload planted in the
detector itself.

## P-5 in detail (the only open proposal)

`public/index.html` uses `hidden` and `aria-hidden` for tab switching and
accessibility. This is the strongest argument for keeping the CSS/attribute rules
at `low`: a scanner that cannot tell a collapsed panel from a concealed
instruction should not be allowed to fail the build on that distinction alone.
Before `--fail-on medium` is even considered, a human should look at the 11 lines
and confirm they are markup the UI toggles at runtime.
