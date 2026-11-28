#!/usr/bin/env python3
"""critic-evidence — repository code graph plus the claim/evidence census.

Remit: every quantitative or capability claim needs a proof pointer.
Read-only: writes only the report path given with `--json`.

    python3 .subagents/critic-evidence/codegraph.py --json reports/latest.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SUB = "critic-evidence"
KIND = "critic"
REMIT = ("Audit quantitative and capability claims for a proof pointer and "
         "reject every claim that has none.")
FOCUS = [
    "README.md", "AGENTS.md", "CHANGELOG.md", "docs/*.md", ".agents/*.md",
    ".agents/docs/*.md", ".agents/skills/*/SKILL.md",
]
# A proof pointer on the line: a command, a path, a URL or a run artefact.
EVIDENCE = ("`", "http", "bash ", "python3 ", "node ", "make ", "./",
            ".sh", ".py", ".c", ".js", ".json")
NUM_RE = (r"\b\d+(?:\.\d+)?\s*(?:tests?|checks?|assertions?|pairs|entries|"
          r"findings|lines)\b|\b\d+\s*/\s*\d+\b")
CLAIM_RE = (r"\b(?:verified|measured|proven|green|passes|passed|"
            r"bit-identical|deterministic|confirmed)\b")
MAX_ROWS = 14


def _load_core():
    here = Path(__file__).resolve()
    root = here.parents[2]
    sys.path.insert(0, str(root / ".subagents" / "tools"))
    import codegraph_core as core  # noqa: E402

    core.repo_root_from(__file__, 2)
    return here, root, core


def _has_evidence(line: str) -> bool:
    return any(marker in line for marker in EVIDENCE)


# Dated records quote the claims of the round that wrote them (the session
# archive, the error log, the changelog, the environment journal). Auditing them
# is auditing history: the first version of this census did exactly that and
# produced 532 hits, almost all of them correct statements about a past state.
DATED = {"CHANGELOG.md", ".agents/errors.md", ".agents/Environment.md",
         ".agents/session.md", ".agents/docs/SESSION-ARCHIVE.md"}


def live_docs(graph):
    # `.subagents/` is excluded as well: the team's own proposals are findings
    # about claims, not claims of the project, and counting them inflated the
    # census with its own output (16 -> 27 bare numeric claims on 2026-10-29).
    return [n for n in graph.docs()
            if n.path not in DATED
            and not n.path.startswith((".agents/docs/", ".subagents/"))]


def _census(graph, core, pattern, label, rows):
    hits = core.find_pattern(graph, live_docs(graph), pattern, max_hits=4000)
    bare = [(p, l, t) for p, l, t in hits if not _has_evidence(t)]
    rows.append(f"{label}: {len(hits)} lines   with a proof pointer on the line: "
                f"{len(hits) - len(bare)}   bare: {len(bare)}")
    for path, line, text in bare[:MAX_ROWS]:
        rows.append(f"  [bare] {path}:{line}  {text}")
    if len(bare) > MAX_ROWS:
        rows.append(f"  ... {len(bare) - MAX_ROWS} more bare lines")
    rows.append("")
    return bare


def extra(graph, core):
    rows = ["scope: live claims only - dated records excluded ("
            + ", ".join(sorted(DATED)) + ", .agents/docs/*)",
            "NOTE: the proof test is a same-line heuristic. A command on the next",
            "line is still proof - clear those by hand before filing a defect.", ""]
    bare_numbers = _census(graph, core, NUM_RE, "numeric claims", rows)
    bare_claims = _census(graph, core, CLAIM_RE, "capability claims", rows)
    rows.append(f"total findings to triage: {len(bare_numbers) + len(bare_claims)}")
    rows.append("severity guide: blocker = a reader would act on it, "
                "major = misleading, minor = imprecise")
    return "evidence census: claims without a proof pointer", rows


def main(argv=None) -> int:
    here, root, core = _load_core()
    parser = argparse.ArgumentParser(prog=f"{SUB}/codegraph.py", description=REMIT)
    parser.add_argument("--json", metavar="PATH",
                        help="write the machine-readable report here (relative to this folder)")
    parser.add_argument("--md-only", action="store_true")
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args(argv)

    graph = core.build_graph(root)
    print(core.render_text(graph, focus=FOCUS, top=args.top, md_only=args.md_only))
    title, rows = extra(graph, core)
    print(core.render_extra(title, rows))

    if args.json:
        path = Path(args.json) if Path(args.json).is_absolute() else here.parent / args.json
        core.write_json(graph, path, focus=FOCUS,
                        extra={"sub": SUB, "kind": KIND, "remit": REMIT,
                               "check": title, "rows": rows})
        print(f"\nreport written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
