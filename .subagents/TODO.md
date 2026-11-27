# `.subagents` pipeline checklist

The reusable run-book for a round that uses the team. The round's own todo list
lives in `.agents/session.md` (this repository has no separate todo tool); this
file is the procedure that produces the evidence.

## Before the first run of any member

- [ ] the member's folder exists with `ORIGINAL.md`, `AGENTS.md`, `SKILL.md`,
      `ERROR.md`, `REQUESTS.md`
- [ ] `ORIGINAL.md` quotes the owner assignment verbatim and states the
      normalised English assignment plus acceptance criteria
- [ ] `ORIGINAL.md` records the creation date and the repository state it was
      created in

## Every run

- [ ] `python3 .subagents/tools/run_all.py` exits 0 (all seven, no retries needed)
- [ ] `reports/latest.txt` and `reports/latest.json` exist for every member
- [ ] `PROPOSALS.md` of every member was written from that report, not from memory
- [ ] every proposal row carries a `file:line`, a command output or a URL
- [ ] no member modified anything outside its own folder
- [ ] `python3 .subagents/tools/check_subagents.py` is green
- [ ] `python3 .subagents/tools/check_subagents.py --self-test` proves the gate
      can fail
- [ ] `python3 .subagents/ai-threat-scan/scan.py --self-test` proves every detection rule
      still fire, and asserts mechanically that **every** rule in `rules_table()` has a
      fixture with a path+line assertion and that the near misses stayed clean (a dead
      rule, or a rule with no fixture, makes the tree scan look green)
- [ ] `python3 .subagents/ai-threat-scan/scan.py . --fail-on high` is green, or
      every high finding was worked: proposed, narrowed in code, or waived in
      place with a reason

## End of the round

- [ ] `critic-final/REVIEW.md` exists with a score and a per-criterion verdict
- [ ] score >= 7/10; below that, the fix list is applied and the critic re-run
- [ ] `.agents/session.md` plan updated (the todo list, step by step)
- [ ] `.agents/errors.md` has an entry for every error hit during the run
- [ ] `.agents/user.md` updated if the owner stated a new standing rule
- [ ] `bash tools/session_start_check.sh` and `bash tools/docs_claim_check.sh` green

## When a member fails

- [ ] the failure is visible in `reports/latest.txt` (attempt number and error)
- [ ] `run_all.py` retried once; a second failure fails the whole run
- [ ] the failure is logged in `.agents/errors.md` with symptom, cause and fix

## Scanner backlog (the NOT-covered rows of the coverage matrix)

These are the classes the scanner deliberately does **not** detect. Each row is
work, not a claim; the matrix with the reasons is in
`.subagents/ai-threat-scan/AGENTS.md` ("Coverage matrix", last table).

- [ ] Decoding deeper than three layers, and unknown ciphers (AES/XXTEA, custom
      substitutions). Shipped in round 18: nested base64/hex/percent/ROT13 up to
      depth 3 with `nested_encoded.md` + `near_nested.md`. Anything beyond that
      needs a decidable rule before it ships - not a bigger number.
- [ ] Homoglyphs outside the built-in table: mathematical alphanumerics
      (U+1D400…), Armenian/Cherokee look-alikes, whole-script substitution.
      Requires importing a real UTS #39 confusables map and a size decision.
- [ ] Payloads in binaries/images/PDFs: separate extraction job, not this scanner.
- [ ] Typoglycemia / scrambled instruction words ("ignroe all prevoius systme
      instructions"): OWASP names the class. Needs a bounded fuzzy match on the
      instruction keywords plus a fixture pair; until then a scrambled instruction
      is a pass.
- [x] Instruction in a comment that addresses an agent: shipped in round 18 as
      `comment-instruction` (low), addressed form only. The broad form was measured
      at 54 legitimate lines and rejected.
