# Requests — `ai-threat-scan`

Questions this sub cannot answer alone (R34/R35, owner decisions, dependency
policy). Format: one block per request, status first, recommendation last. An
answered request keeps its answer, because the next agent inherits the decision,
not the discussion.

| # | Question | Status |
|---|---|---|
| R-1 | Should the CI gate fail on `medium` too, or stay on `high`? | open |
| R-2 | Is a second-opinion scanner (Cisco skill-scanner, Semgrep bidi rule) worth an extra CI job? | open |
| R-3 | Are binaries, images and PDFs in scope? | open |
| R-4 | Should the scanner read Git history for payloads that were committed and removed? | open |
| R-5 | Who may waive a `high` finding — any agent, or only the owner? | open |
| R-6 | Should the waivers inside `scan.py` be constrained mechanically to pattern/fixture lines? | implemented (round 16) — not as a line region but as exact rule id + written reason + inventory |
| R-7 | Is a per-line waiver on a document that quotes a payload (threat model, review) acceptable policy, or should quotes be transformed instead? | open |

---

## R-1 — fail on `high` or on `medium`?

**Why it matters.** The tree currently has 12 `low` notes (all legitimate UI:
`hidden` attributes and one `display:none` marker in `public/style.css`). Lowering
the threshold now would make CI red on a clean tree, which teaches people to
ignore the gate.

**Recommendation.** Keep `--fail-on high` (the default). Revisit after the `low`
notes are classified per file: if the residue is provably UI, the threshold can
move to `medium` and `low` can be printed only.

## R-2 — second-opinion scanner in CI?

**Why it matters.** Independent tools (Cisco skill-scanner, NVIDIA SkillSpector,
Semgrep's bidi rule) would catch a rule we did not think of. All of them add a
Node/Python dependency tree and a second supply chain — which is itself the class
of risk this job exists to reduce.

**Recommendation.** No, until an installation can be pinned and reproduced
offline; use them manually during a security round and record the version tested.

## R-3 — binaries, images, PDFs?

**Why it matters.** A payload can live in a PNG chunk, a PDF annotation or a
`.docx` body. Current behaviour: binary detection by NUL byte, 2 MiB cap, and the
skip counts are printed.

**Recommendation.** Out of scope for this scanner, in scope for a separate
extraction job if the repo ever carries such files as *input to an agent*. Today
it carries none, so the risk is theoretical.

## R-4 — Git history?

**Why it matters.** A payload committed and then removed is still in history, and
an agent that runs `git log -p` reads it.

**Recommendation.** Out of scope: history is immutable data with a different
review model (it cannot be fixed by editing a file). If it matters, scan the diff
of a PR inside CI, not the archive.

## R-5 — which findings may be waived, and by whom?

**Why it matters.** A waiver is the only way to silence a `high` finding, so the
rule about waivers is the whole security value of the gate.

**Recommendation.** `high` waivers need the owner's explicit approval recorded in
`.agents/session.md`; `medium`/`low` waivers need a written reason on the line -
which round 16 now enforces mechanically (exact rule id plus reason of at least 20
characters, otherwise nothing is suppressed). So what is left open here is only
*who* may approve a `high` waiver, not whether a waiver needs a reason.

## R-6 — constrain the scanner's own waivers mechanically

**Implemented (round 16).** The risk was never the *place* of a waiver but its
*reach*, so the mechanism was bounded instead of the line numbers. The rule,
enforced in `scan.py` and pinned by six self-test fixtures:

1. a marker covers only the rule ids it names, parsed against the rule table -
   `allow css-hidden-content` never hides a `invisible-tag-block` hit;
2. the text after the ids must be at least 20 characters and not a placeholder
   (`n/a`, `todo`, `false positive`, …), otherwise nothing is suppressed;
3. a marker that names a known rule but suppresses nothing because of (2) leaves
   the finding in place and adds one `waiver-invalid` low note at that line;
4. every waiver that did suppress is printed and serialised with `file:line`,
   rule id and reason, so the report shows what was hidden and why.

A waiver is therefore valid on **any** line and still cannot become a blind spot:
a payload inside `scan.py` under a mismatched or unreasoned waiver exits 1 with the
file named (plants A and B, round 16), and a marker copied into an ordinary file
behaves identically (plant C).

**Declined alternative:** requiring every marker to sit inside a fixed region of
`scan.py` (`SECRECY` … `self_test()`). It would turn a legitimate quote in the
threat model into a hard error, it would need a line map that itself drifts, and
it rejects nothing that (1) and (2) accept on the current tree.

**Remaining, and yours to decide:** should the region check be added *on top* as a
defence in depth, knowing it will fail the build whenever a doc quote gains a
waiver? Recommendation: no - the semantic bound is the one that survives edits to
line numbers.

## R-7 — quoting a payload in documentation

**Why it matters.** The threat model, the review and the error logs quote
patterns; each quote needs a waiver, and waivers in prose are the easiest place
to hide a real payload. The alternative — transforming quotes (e.g. describing
the download-to-shell shape without the pipe operator) — makes the documentation less useful for a reader
who wants to recognise the shape.

**Recommendation.** Keep visible quotes plus a waiver whose reason names the
class and the source, and require that a quote never spans an executable line in
a fenced block that a reader could copy-paste and run by accident. Reviewed by a
human at the point of the waiver, not by the scanner.
