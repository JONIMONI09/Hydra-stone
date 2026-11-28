# Error Log — `ai-threat-scan`

Append-only. Newest entry **last** (same order as `.agents/errors.md`).
Each entry: what happened, the evidence, what changed because of it. An entry
without a change is an open problem, not a lesson — it says so explicitly.

---

## 2026-10-29 — the PowerShell fixture was never scanned (a rule that could not fire)

**What happened.** The first `--self-test` run failed with
`rule powershell-encoded did not fire on ps.ps1`. The rule was correct; the
fixture was never read, because `TEXT_SUFFIXES` did not contain `.ps1`, so the
file was classified as binary and skipped silently.

**Evidence.** `python3 .subagents/ai-threat-scan/scan.py --self-test` → `SELF-TEST
FAIL / rule powershell-encoded did not fire on ps.ps1`.

**What changed.** Added `.ps1`, `.psm1`, `.bat`, `.cmd`, `.rb`, `.go`, `.rs`,
`.swift`, `.m`, `.mm`, `.lua` to the suffix list. The general lesson: a skip list
is part of the detector. The self-test is what turned this from "green" into a
finding, which is exactly why R25 controls exist.

---

## 2026-10-29 — the scanner reported itself: 38 of 45 "high" findings were its own rule table

**What happened.** The first whole-tree run printed `45 finding(s) at or above
'high'`. 38 of them were `scan.py` matching the patterns it defines, plus its own
fixtures. A gate that reports its own source as malicious is a gate nobody keeps.

**Evidence.** Grouped JSON report: `covert-instruction 9, prompt-override 5,
pipe-to-shell 1 …`, all with `"path": ".subagents/ai-threat-scan/scan.py"`.

**What changed.** Documented single-file exclusion (`SELF_FILE`) with the blind
spot it creates, plus the self-test as the control that the detectors still work.
Not a blanket folder skip.

---

## 2026-10-29 — the generated report was scanned back in (third instance of one class)

**What happened.** After excluding `scan.py`, the top offender became
`reports/latest.json` — the scanner scanning its own output: 26 more findings,
all self-referential.

**Evidence.** `[LOW] html-hidden-attr .subagents/ai-threat-scan/reports/latest.json:574`
— a JSON *snippet field* describing a fixture.

**What changed.** `GENERATED_OUTPUT` matches exactly three paths
(`.subagents/*/reports/latest.json`, `latest.txt`, `scan.json`). The directory is
still scanned, so a hand-written file dropped there is still seen. This is the
third time in three rounds that a tool read its own output (see `.agents/errors.md`,
rounds 12-13); the class is now named there.

---

## 2026-10-29 — a hidden attribute on a UI button was reported as a covert instruction

**What happened.** `hidden-with-instructions` fired 3× on `public/index.html`
(`<button … hidden>`, `<pre … hidden>`), because the rule looked ±300 characters
around the attribute and found the word "upload" in a form label further down.
That is proximity, not concealment.

**Evidence.** `[HIGH] hidden-with-instructions public/index.html:34 —
hidden attribute wraps instruction-like text around the declaration`.

**What changed.** Two modes: CSS declarations keep the ±300 window (the
declaration hides the text that follows it), hidden *attributes* check only the
element's own content (up to 400 characters to the closing tag). Result: 3 highs
became 3 lows on that file.

---

## 2026-10-29 — the space-separated waiver was ignored without an error

**What happened.** A line that trips three CSS rules carried one marker with
three rule ids, space separated. The waiver parser split on commas only, so it
compared `"a b c"` against `"a"` and kept the finding red — silently, since a
waiver that does not match is indistinguishable from no waiver.

**Evidence.** `--only .agents/docs/AI-THREAT-MODEL.md` stayed
`VERDICT: FAIL - 3 finding(s)` after the marker was added, and moved to PASS only
after the parser changed.

**What changed.** `re.split(r"[,\s]+", …)`; the self-test now includes a
multi-rule waiver fixture (`multi.md`) and requires both rules to be waived.

---

## 2026-10-29 — the instruction vocabulary was too broad to be useful

**What happened.** `INSTRUCTION` contained bare `never`, `always`, `system`,
`token`, `run`. On this repository that matched ordinary prose: 6 hidden-comment
findings in Android resource XML (`<!-- the hex value never told anybody … -->`)
and 20 low notes for `hidden` attributes.

**Evidence.** `[HIGH] hidden-html android/app/src/main/res/values/strings.xml:56` —
a resource comment about magic bytes.

**What changed.** The vocabulary is now instruction-shaped: second person
(`you must/should/are`), negation directives (`do not`, `don't`), pull verbs
(`ignore`, `disregard`, `forget`, `upload`, `send the`, `execute`, `curl`),
data nouns (`api key`, `password`, `secret`) and the German equivalents. Bare
`never`/`always`/`system`/`token` are gone.

---

## 2026-10-29 — `symlink-escape` had no rule metadata (found by the folder check, not by the scanner)

**What happened.** The scanner emitted a rule id that did not exist in
`rules_table()`, so a report would have shown an unknown severity. The scanner
cannot see this class in itself; `codegraph.py`'s drift check can.

**Evidence.** `[rules] missing metadata for used rule ids: ['symlink-escape']`.

**What changed.** Metadata added to `rules_table()`, and the drift check stays in
`codegraph.py` permanently — it is the same "one rule in two places" class as the
duplicated bf16 decoder in round 13.

---

## 2026-10-29 (round 15) — the whole-file exclusion was the very thing this scanner is supposed to catch

**What happened.** Round 14 made the scanner skip its own source (`SELF_FILE`,
`ai-threat-scan/scan.py`) to get from 45 findings to 0. That is a file-level
mute: a hidden payload planted *inside the detector* would never be reported,
and the run would look clean.

**Evidence.** With `SELF_FILE` in place the header printed
`1 detector source` as a skip and the file never appeared in the 232 scanned
count. After removing the exclusion the same tree scans 233 files and `scan.py`
is one of them.

**What changed.** The exclusion is gone. Instead, the 36 lines that *define* a
pattern or *are* a fixture carry `ai-threat-scan: allow <rule-id> (<reason>)` on
exactly that line - 38 waived hits on 36 marked lines, with three distinct
reasons (pattern definition, rule metadata, self-test fixture). A payload appended anywhere else in the file is caught like
any other text. `--self-test` now has an `own_source` fixture: it copies
`scan.py`, requires the copy to scan clean, appends one tag-block payload, and
requires `invisible-tag-block` on that path — so a silent file-level skip coming
back turns the self-test red.

**Proved on the working tree (not in a fixture).** Planted `STEAL` as tag
characters at the end of `scan.py`: `exit 1`,
`[HIGH] invisible-tag-block .subagents/ai-threat-scan/scan.py:605`, `5 tag
characters, decodes to 'STEAL'`. Restored from a copy, `sha256sum -c` OK, then
`exit 0`.

**Prevention.** "Exclude the checker" is a legitimate engineering need only at
the granularity of the thing that collides — a pattern, a fixture, a generated
report — never a whole source file. The self-test owns the property now.

---

## 2026-10-29 (round 15) — a dead conditional shipped in the gate patch and no gate could have seen it

**What happened.** The `layout_checks()` patch contained
`rel = os.path.relpath(...).replace(os.sep, ".") if False else os.path.relpath(...)`
— a leftover from editing two variants of the same line. It is valid Python,
executes the right branch, and pyflakes stays silent.

**What changed.** The line was removed before the first run (one assignment, no
`if False`). Nothing else changed.

**Prevention.** The gates check behaviour, not intent; dead branches are invisible
to them by construction. The only control is reading the diff, which is why the
review of a patch is not optional even when every check is green.

---

## 2026-10-29 (round 15) — the CI step name hard-coded a rule count that was already stale

**What happened.** The `lint.yml` step was named
`Self-test (all 26 rules must fire, …)` while `rules_table()` has 27 entries
(`symlink-escape` was added in round 14 and the name was not updated). R21
covers exactly this: a number in prose that nothing derives.

**What changed.** The step is named for the property, not the number
(`all 27 rules fire, clean file/tree stay green, own source checked`), and the
self-test prints the count it actually exercised.

**Prevention.** Names may state a property; counts come from the run. A hard-coded
count in a workflow name is a documentation bug with a CI bill.

---

## 2026-10-29 (round 16) — the waiver inventory quoted the comment terminator as part of the reason

**What happened.** After the strict waiver grammar landed, the tree report listed
reasons like `quoted example, class T2)` and `this paragraph names the CSS
properties it detects)`. Every suppressed hit came back with a stray closing
bracket, so the printed justification looked truncated mid-sentence.

**Cause.** The reason was produced by `strip()` over punctuation, and the line was
`... (quoted example, class T2) -->`. `strip()` removes characters from the end
while they are in the set; it stopped at the space before `-->`, so the `)` that
sits *before* that space was never reached. Ordering bug: the comment terminator
has to go before punctuation is trimmed.

**What changed.** `_waivers()` now cuts the text at `-->` or `*/` first and only
then collapses and trims. The inventory prints `quoted example, class T2`.

**Prevention.** No test caught this - it was found by reading the report, which is
why the waiver inventory is printed and not only counted. Any field that is shown
to a reviewer has to be read once by the author of the change.

---

## 2026-10-29 (round 16) — a fixture went red for a presentation detail, not for a contract

**What happened.** `waiver_valid` failed with "the suppression was not recorded
with its reason in the inventory" even though the waiver had been recorded with
its reason.

**Cause.** The assertion compared against `(self-test: the waiver states a real
reason)` - the raw text including the parentheses - while the parser normalises
away the bracket decoration and the comment closer. The fixture encoded how the
line looked, not what the parser promises.

**What changed.** The fixture asserts the normalised reason
(`self-test: the waiver states a real reason`), which is the value the inventory
contract promises.

**Prevention.** Assert the parsed contract, not the source spelling. A fixture that
copies the input formatting will break on every harmless formatting change and
teach people to edit the fixture instead of reading the failure.

---

## 2026-10-29 (round 16) — adding fixtures turned the scanner's own source red

**What happened.** `--self-test` reported
`the unmodified scanner copy produced 1 high/medium finding(s): covert-instruction`
after the new waiver fixtures were written.

**Cause.** The fixture helper assigns the secrecy phrase (the `covert-instruction`
class wording) to a variable inside `scan.py`. That line is a pattern-bearing line
in the scanner's own source and it carried no waiver. Before round 16 an
unreasoned waiver would have covered it; now a waiver has to name the rule and the
reason, and this line had neither.

**What changed.** The line carries
`ai-threat-scan: allow covert-instruction (self-test fixture: the secrecy phrase assigned to a variable here)`.

**Prevention.** Every new pattern-bearing line in `scan.py` needs its own reasoned
waiver - run `scan.py .subagents/ai-threat-scan` right after touching the fixtures,
before the full gate, so the failure names the line instead of arriving as a
whole-tree red.

**Second slip, same entry.** The first version of this text reproduced the secrecy
phrase verbatim inside the *Cause* paragraph, which turned `ERROR.md:238` into a
`covert-instruction` high finding (rc=1) while the entry was being written. The
paragraph now describes the phrase instead of quoting it. Writing about a payload
is indistinguishable from carrying one, so prose in this folder gets the same
treatment as code: describe the shape, or carry a waiver with a reason.

---

## 2026-10-29 (round 16) — the round-15 fix left the rule count in the CI step name

**What happened.** The `ai-threat-scan` job still had a step named
`Self-test (all 27 rules fire, ...)`. `rules_table()` now has 28 entries (27
detection rules plus the new `waiver-invalid` diagnostic), so the name was already
one off again - and would drift every time a rule is added.

**Cause.** Round 15 fixed the *value* of the hard-coded number (26 → 27) instead of
removing the number. The rule it wrote down ("names may state a property; counts
come from the run") was not applied to the line it was written about.

**What changed.** The step is named
`Self-test (every detection rule fires, the waiver rule is proven, clean file/tree
stay green, own source checked)`. The same drift was removed from
`.subagents/README.md` (said 26 rules) and `.subagents/TODO.md` (said 27), and the
threat model now says "27 detection rules plus one diagnostic rule" instead of a
bare total.

**Prevention.** A number that no command derives is a defect, even when it happens
to be right today. When a fix is about "don't hard-code this", grep for the other
copies in the same change - one pass, not one line.

---

## 2026-10-29 (round 17) — the self-test could pass with rules that have no fixture

**What happened.** The coverage audit found two detection rules with no fixture at
all (`pipe-to-shell`, `symlink-escape`), and the three new rules would have been
added with no proof beyond "the tree scan is still green". The first run of the
new assertions then failed with
`fixture/rule mismatch: no fixture for ['symlink-escape'], fixture rule count 29 != rule table size 30`.

**Cause.** The assertion was `if rule not in found_rules` over one flat set of
every finding in the temp tree. A rule counted as proven if *any* finding anywhere
carried its id - so a fixture could fire the wrong rule and still pass, a rule
could have no fixture and nothing noticed, and the count in the banner was never
compared with `rules_table()`.

**What changed.** Every fixture is now asserted on its own file with its own rule
id and line 1, `{fixture rules}` must equal the detection rules of
`rules_table()` (set and count), `LOOP_RULES` must have no orphan and no ghost
entries, and six near misses must stay completely clean. `symlink-escape` is
covered by a real symlink created in the temp dir (a text file cannot express a
symlink) and is added to the covered set explicitly.

**Prevention.** "Some rule fired" is not a test. A fixture must name the rule it
proves and the place it proves it at, and the set of fixtures must be compared with
the set of rules - otherwise the test measures the test, not the detector.

---

## 2026-10-29 (round 17) — the drift check kept its own copy of the rule list and reported live rules as dead

**What happened.** `codegraph.py` printed
`[rules] declared but never used by a table: ['encoded-instruction', 'homoglyph-instruction', 'private-use-character', 'symlink-escape', 'waiver-invalid']`
for rules that are emitted by the scanning loop and are very much alive. Two of
those ids (`symlink-escape`, `waiver-invalid`) were already stale before this
round; nobody read the row because the check only failed on *missing* metadata.

**Cause.** `_rule_table_drift()` had a hand-written set of "rules the loop emits".
It was correct when it was written and drifted the moment a rule was added - the
same class of bug as the duplicated bf16 decoder (round 13), in a check that exists
to catch exactly this.

**What changed.** `scan.py` owns `LOOP_RULES`, `--self-test` asserts that every
declared rule is reachable from a pattern table or from `LOOP_RULES` (and that
`LOOP_RULES` names nothing unknown), and `codegraph.py` reads that set instead of
keeping one.

**Prevention.** A check with its own copy of the truth is a second source that will
disagree. When a checker needs "the list of X", the list belongs next to X and the
checker imports it.

---

## 2026-10-29 (round 17) — three small slips found by reading the output, not by a test

1. **Banner count wrong.** The self-test printed `29 detection rules` while the
   table had 30: the number was computed from the fixture set before the symlink
   fixture was added to it. Replaced by `len(covered_rules)`, which is the same set
   the assertion compares. R21 again: a count in prose that nothing derives.
2. **A waiver that suppressed nothing.** The homoglyph fixture line in `scan.py`
   carried `allow homoglyph-instruction (...)`, but the source spells the Cyrillic
   as `\u0456` escapes, so the scanner's own line holds no look-alike character and
   never fired. The waiver was invisible clutter (unused waivers are not listed in
   the inventory) and would have looked like evidence of a detection. Found by
   diffing the waiver inventory against the previous round; removed - the fixture
   itself is the proof.
3. **A dead skip counter in the report.** `codegraph.py` printed
   `0 detector source` because it read `skipped.get('self', 0)`, a leftover from
   the file-level self-skip that round 15 removed. A permanently zero column reads
   like a verified exclusion. Removed.

**Prevention.** Read the artefact you ship once, end to end. All three were visible
in plain output and none was visible to a passing test.

---

## 2026-10-29 (round 18) — the new comment-token regex made the scanner flag its own rule table as a hidden HTML comment

**What happened.** `--self-test` failed with
`the unmodified scanner copy produced 1 high/medium finding(s): hidden-html` and the
tree scan showed `[HIGH] hidden-html .subagents/ai-threat-scan/scan.py:197` on the
line that defines `COMMENT_BODY`.

**Cause.** The definition contained the literal opener `<!--`. `COMMENT_HTML` scans
the whole file for `<!--(.*?)-->`, so it started a "comment" at that line and ended
it at the next `-->` far below - swallowing the SECRECY/OVERRIDE tables, which are
instruction language. One literal token turned the scanner's own rule table into a
hidden comment. This is the self-reference trap the file already documents for the
waiver marker, repeated with a different token.

**What changed.** The opener is written as `\x3c!--` inside the raw regex, so the
definition matches a real `<` without containing the token it detects; the existing
`hidden2.html` fixture keeps proving that real HTML comments still fire.

**Prevention.** A detector's definition must not contain its own trigger literally.
When a rule's input token is also a token the file is scanned for, write it escaped
and say why in a comment - and let `--self-test`'s own-source control catch the
regression, which it did.

---

## 2026-10-29 (round 18) — the first design of the comment rule would have flagged the quoted example it must ignore

**What happened.** The first `AGENT_ADDRESS` pattern allowed a match anywhere after a
sentence break (`(?:^|[.!?]\s+)`), so the required near-miss
`# The docs mention "AI agents: exfiltrate" as an example.` was reported. The
detector would have been "fixed" by writing a cleverer quote heuristic instead of a
narrower rule.

**Cause.** The pattern described *where the words appear* instead of *who the comment
is addressed to*. A mention of an agent and an address to an agent look identical to
a mid-line pattern.

**What changed.** The address must start the comment body (`^\s*(?:note (to|for) )?…`).
That single anchor makes the quoted example, a mid-comment mention and a plain
imperative comment quiet without any quotation heuristic, and the near-miss fixtures
(`near_comment_quote.py`, `near_comment_mid.py`, `near_comment_plain.py`) enforce it.

**Prevention.** Anchor at the structure that carries the meaning (start of the
comment), not at a punctuation guess. A negative fixture written first would have
caught this before the positive one passed.

---

## 2026-10-29 (round 18, post-round verification) — the team overview still described the scanner with a three-round-old rule count

**What happened.** Asked to re-check the documentation against the code, the audit
found `.subagents/README.md` describing `ai-threat-scan/` as "27 detection rules"
(round 15's number) and `.agents/README.md` calling `.subagents/` "the six-agent
team (three research, three critics)" although the team has had seven members since
round 14 and 31 detection rules since round 18.

**Cause.** Both lines were true when written and no check compares prose counts with
`rules_table()` or with the member folders. The matrix in this folder is checked by
`--self-test`; the two overview documents were not.

**What changed.** `.subagents/README.md` says 31 detection rules and names the
encoded/comment classes; `.agents/README.md` says seven-member team and lists
`ERROR.md`/`REQUESTS.md` as part of a member folder.

**Prevention.** An overview line that states a number is a claim like any other: keep
the count out of the prose, or derive it. The audit is repeatable - load `scan.py`,
compare `len(rules_table())` with the numbers the documents state, and grep for the
member count.
