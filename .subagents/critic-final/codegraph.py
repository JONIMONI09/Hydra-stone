#!/usr/bin/env python3
"""critic-final — repository code graph plus the team preflight.

Remit: preflight all six sub-agent folders, then score the round 1-10.
Read-only: writes only the report path given with `--json`.

    python3 .subagents/critic-final/codegraph.py --json reports/latest.json
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SUB = "critic-final"
KIND = "critic"
REMIT = ("Preflight all seven sub-agent folders and grade the round against the "
         "rubric; below 7/10 the round is blocked.")
# The seventh member (ai-threat-scan) was added the same day this folder was
# created; ORIGINAL.md is immutable and still says "six", so the preflight covers
# every folder that exists and REVIEW.md states which rubric line that satisfies.
TEAM = ("web-source-verifier", "web-spec-conformance", "web-tooling-scout",
        "critic-evidence", "critic-architecture", "critic-final", "ai-threat-scan")
REQUIRED = ("ORIGINAL.md", "AGENTS.md", "SKILL.md", "codegraph.py",
            "ERROR.md", "REQUESTS.md")
FOCUS = [".subagents/", ".agents/session.md", ".agents/rules.md"]


def _load_core():
    here = Path(__file__).resolve()
    root = here.parents[2]
    sys.path.insert(0, str(root / ".subagents" / "tools"))
    import codegraph_core as core  # noqa: E402

    core.repo_root_from(__file__, 2)
    return here, root, core


def frontmatter(path: Path):
    """(ok, detail) for the Agent Skills frontmatter rules R29/R30."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return False, f"unreadable ({exc.__class__.__name__})"
    if not text.startswith("---\n"):
        return False, "no frontmatter block"
    end = text.find("\n---", 4)
    if end < 0:
        return False, "unterminated frontmatter"
    block = text[4:end]
    try:
        block.encode("ascii")
    except UnicodeEncodeError:
        return False, "frontmatter is not ASCII"
    name = re.search(r"^name:\s*([\w.-]+)\s*$", block, re.MULTILINE)
    desc = re.search(r'^description:\s*"(.+)"\s*$', block, re.MULTILINE)
    if not name:
        return False, "no name field"
    if not desc:
        return False, "no quoted description"
    return True, name.group(1)


def extra(graph, core):
    rows, ready, problems = [], 0, 0
    root = graph.root
    for name in TEAM:
        folder = root / ".subagents" / name
        rows.append(f"[{name}]")
        if not folder.is_dir():
            rows.append("  MISSING folder")
            problems += 1
            continue
        missing = [f for f in REQUIRED if not (folder / f).is_file()]
        rows.append("  required files: " + ("all present" if not missing
                                            else "MISSING " + ", ".join(missing)))
        skill_ok, detail = frontmatter(folder / "SKILL.md")
        match = "ok" if (skill_ok and detail == name) else f"name mismatch ({detail})"
        rows.append(f"  SKILL.md frontmatter: {'valid' if skill_ok else 'INVALID'} - {match}")
        report = folder / "reports" / "latest.json"
        rows.append(f"  reports/latest.json: {'present' if report.is_file() else 'MISSING'}")
        proposals = folder / "PROPOSALS.md"
        size = proposals.stat().st_size if proposals.is_file() else 0
        rows.append(f"  PROPOSALS.md: {'present' if size else 'MISSING'} ({size} B)")
        books = {}
        for book in ("ERROR.md", "REQUESTS.md"):
            path = folder / book
            books[book] = path.stat().st_size if path.is_file() else 0
            rows.append(f"  {book}: {'present' if books[book] else 'MISSING'} ({books[book]} B)")
        ok = (not missing) and skill_ok and detail == name and report.is_file() \
            and size > 0 and all(books.values())
        ready += 1 if ok else 0
        problems += 0 if ok else 1
        rows.append("")

    rows.append(f"folders ready: {ready}/{len(TEAM)}")
    rows.append("")
    rows.append("rubric (see ORIGINAL.md): structure 2, skills 1, codegraph 2, "
                "evidence 2, protocol 2, no-stubs 1")
    rows.append("this preflight only measures criteria 1-3 and 6; criteria 4-5 "
                "need the sampling step in SKILL.md")
    rows.append("")
    session = graph.read(".agents/session.md")
    # Anchor on a real heading: `str.split("## Round")` also splits on the words
    # inside a sentence, and the R33 marker line of this round happens to quote
    # the heading (first run reported MISSING while gate 1j was green).
    sections = re.split(r"(?m)^## Round", session)
    marker = "**Session start (R33):**" in sections[-1]
    rows.append(f"R33 marker in the current round section: "
                f"{'present' if marker else 'MISSING'}")
    rows.append(f"open checkboxes across the tree: {len(graph.open_items)}")
    for path, line, text in graph.open_items[:10]:
        rows.append(f"  [open] {path}:{line}  {text}")
    return "team preflight (rubric criteria 1-3, 6)", rows


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
