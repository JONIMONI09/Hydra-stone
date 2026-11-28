---
name: web-tooling-scout
description: "Audit the verification toolchain: which tools/ gate scripts CI really runs, which documented commands point at missing files, and which tool has no tested install path in Environment.md."
---

# Web Tooling Scout

## When to use

Use when a documented command, gate or tool path may be stale, or before adding a new gate. Not for judging code quality.

Use before adding a gate, after deleting or renaming a tool, when a documented
command fails for a reader, or when a new sandbox needs its install paths
recorded.

## Why this exists

Two silent failure classes cost this project time already:

- a gate that nobody calls (decoration, the "gate that never goes red"
  problem R25 exists for), and
- a documented command that points at a file that no longer exists — the
  reader's copy-paste fails and the doc looks authoritative while being wrong
  (the round-10 `timeout`/`env` recipe bug was this class).

## Procedure

1. **Wiring.** `python3 codegraph.py` prints every `tools/*.sh` with whether any
   workflow file mentions it. Anything unreferenced is then checked against the
   `Makefile` and the docs before being called orphaned.
2. **Commands.** Every `tools/...` path mentioned in a `.md` is checked for
   existence. A missing one is a documentation defect with a `file:line`.
3. **Installs.** Every `pip install` / `npm ci` / `apt-get install` in a
   workflow is listed, so a reader can reproduce CI locally without guessing.
4. **Coverage.** The script checks whether `.agents/Environment.md` mentions the
   core toolchain (gcc, clang, cppcheck, python3, node, zig, kotlinc, …). A tool
   a gate needs with no recorded install path is a trap for the next agent.
5. **Web check.** For each gap, look up the official install command and record
   it with the URL — primary source only (R26).

## Evidence rules

- "Gate X is not wired" requires the search that found nothing, not an
  impression.
- "Command Y is wrong" requires the path check plus the documented line.
- "Blocked" requires the attempted command and its error (R32).

## Anti-patterns

- Installing a tool and calling the gate green without running it.
- Proposing a new gate without a negative control (R25).
- Editing `Environment.md` outside your own section.
