# Requests — `critic-architecture`

| # | Question | Status |
|---|---|---|
| R-1 | Is the duplicated `_load_core()` block in every sub script acceptable, or should it become one shared bootstrap? | open |
| R-2 | Is a thin adapter that differs only by exception type "duplication" or "an interface"? | open |

## R-1 — the bootstrap block

**Why it matters.** Seven `codegraph.py` files each carry a ~8-line `_load_core()`.
That is duplication by the letter of the rule, and deliberate: each sub must run
standalone, from its own folder, without the others installed.

**Recommendation.** Keep it, and record the exception in the skill so the next
architecture pass does not re-report it as a finding. The alternative — a shared
import path — makes a sub unusable when the shared file is missing, which is
exactly the failure the read-only contract tries to avoid.

## R-2 — adapters

**Recommendation.** An adapter that only maps an error type is an interface, not
a copy: the rule lives in one place. Document the line, or the same finding is
reported every round.
