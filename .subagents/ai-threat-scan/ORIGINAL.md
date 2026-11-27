# ORIGINAL.md — `ai-threat-scan`

> Created **before this sub-agent's first run** (owner directive 2026-10-29).
> Immutable assignment record: never edited after creation; a changed remit
> gets a new `ORIGINAL-<date>.md`.

| Field | Value |
|---|---|
| Sub-agent | `ai-threat-scan` |
| Kind | security scanner (7 of 7) — the only member allowed to write code |
| Created | 2026-10-29 |
| Created by | parent agent (round 14) |
| Repo state | branch `freebuff/6daeacda62104e261f2b28ce`, base `94f8e08` + rounds 12-13 uncommitted |
| Web access | allowed and expected: the rule set is updated from published sources |

## Original owner assignment (verbatim, German)

> "also einen Sub Agenten der Nach Schadcode und nach Schadanweisung für KI erkennt also schaut in die Dateien rein darf ein py selber schreiben um Sachen zu scannen etc also alles an Dateien markdowns etc ! schaue im Web 2026+ und neuer nach er darf seine Tools updaten und upgraden ! keine Schadsoftware etc ! suche nach unsichtbaren Zeichen Instruktionen die bösen Willen haben 'Nicht User sagen' etc !!! mache Sicherheitsregeln !!! Also AI soll im Web nach Anweisungs Schadware suchen und Tools die prüft etc !! baue es dann in die CI ein"

> "Also jeder Sub hat Error.md und so in ihren Ordnern etc"

> "Subs können Anfragen machen und bei der Klarstellung helfen !!!"

## Normalised assignment (English)

Look inside the files, not at their names. Find malicious code **and**
malicious instructions aimed at an AI — including instructions a human cannot
see (invisible characters) and instructions that tell the model to hide what it
does from the user. Write the detector yourself in Python (stdlib, offline), look
up the current threat landscape and the existing scanners on the web (2026 and
later), keep the rule set upgradeable, and wire the detector into CI. Do not
create or ship malware: the fixtures are synthetic, minimal and never executable.
Maintain `ERROR.md` (what went wrong, and what changed because of it) and
`REQUESTS.md` (questions that need the owner or the parent agent to decide).

## Deliverables

| File | Meaning |
|---|---|
| `scan.py` | the scanner: 26 rules, severities, in-line waivers, `--json`, `--fail-on`, `--self-test` |
| `AGENTS.md` | the contract this sub works under |
| `SKILL.md` | reusable procedure (Agent Skills format, R29/R35) |
| `codegraph.py` | read-only repository graph + this folder's own security check |
| `ERROR.md` | the error log of this sub (append-only) |
| `REQUESTS.md` | open and answered questions to the owner/parent |
| `PROPOSALS.md` | proposals only — **no edits outside this folder** |
| `reports/latest.{txt,json}`, `reports/scan.json` | generated evidence of the last run |

## Acceptance criteria

1. Every rule is proven by `--self-test`; a rule that stops firing turns the
   self-test red and therefore the CI job red.
2. The scanner is read-only: no writes to the tree, no network, no subprocess.
3. A clean run is reported as limited evidence, never as "safe".
4. Every waiver has a written reason on its own line and appears in the report.
5. The rule set carries sources (`.agents/docs/AI-THREAT-MODEL.md`) and can be
   extended without touching the scanning loop.
