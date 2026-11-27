#!/usr/bin/env python3
"""web-tooling-scout — repository code graph plus the toolchain audit.

Remit: gate wiring, documented commands, install paths, tool coverage.
Read-only: writes only the report path given with `--json`.

    python3 .subagents/web-tooling-scout/codegraph.py --json reports/latest.json
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SUB = "web-tooling-scout"
KIND = "web-research"
REMIT = ("Audit the verification toolchain: which tools/ gate scripts CI really "
         "runs, which documented commands point at missing files, and which "
         "tool has no tested install path.")
FOCUS = [
    ".github/workflows/*.yml", "tools/*.sh", "tools/*.py", "tools/*.js",
    "Makefile", ".agents/Environment.md", ".agents/skills/engine-ci-verify/SKILL.md",
    "AGENTS.md",
]
# The lookbehind keeps `.subagents/tools/x.py` from being read as
# `tools/x.py` - the first version of this check reported the scanner's own
# path as a missing file.
TOOL_RE = r"(?<![\w./-])(tools/[\w./-]+\.(?:sh|py|js))"
INSTALL_RE = r"(?:python3? -m )?pip3? install|npm (?:ci|install|i)\b|apt-get install|brew install|pipx run"
TOOLCHAIN = ("gcc", "clang", "cppcheck", "clang-tidy", "python3", "node",
             "zig", "kotlinc", "shellcheck", "actionlint", "bandit", "pyflakes",
             "qemu-aarch64", "javac")
MAX_ROWS = 30


def _load_core():
    here = Path(__file__).resolve()
    root = here.parents[2]
    sys.path.insert(0, str(root / ".subagents" / "tools"))
    import codegraph_core as core  # noqa: E402

    core.repo_root_from(__file__, 2)
    return here, root, core


def extra(graph, core):
    rows = []
    gates = core.gate_wiring(graph)
    unwired = [path for path, wired in gates if not wired]
    rows.append(f"gate scripts in tools/: {len(gates)}   referenced by a workflow: "
                f"{len(gates) - len(unwired)}   not referenced: {len(unwired)}")
    rows.append("")
    rows.append("gate wiring (script, referenced by a workflow file):")
    for path, wired in gates:
        rows.append(f"  {'wired   ' if wired else 'CHECK   '} {path}")
    rows += ["", "for every CHECK above: verify Makefile / documented manual use "
                 "before calling it orphaned"]

    workflows = [n for n in graph.nodes if n.path.startswith(".github/workflows/")]
    installs = core.find_pattern(graph, workflows, INSTALL_RE, max_hits=80)
    rows += ["", f"tool install commands in workflows: {len(installs)}"]
    for path, line, text in installs[:MAX_ROWS]:
        rows.append(f"  {path}:{line}  {text}")

    # Dated records are not instructions: an error entry that names
    # `tools/foo.sh` as a hypothetical example, and the append-only session
    # archive, must not be reported as broken commands (same exclusion
    # tools/docs_claim_check.sh makes for the archive).
    HISTORICAL = {".agents/errors.md", ".agents/docs/SESSION-ARCHIVE.md",
                  ".agents/docs/RESEARCH-LOG.md", "CHANGELOG.md"}
    live_docs = [n for n in graph.docs() if n.path not in HISTORICAL]
    refs, missing, seen = core.find_pattern(graph, live_docs, TOOL_RE, max_hits=2000), [], set()
    for path, line, text in refs:
        for ref in re.findall(TOOL_RE, text):
            if ref in seen:
                continue
            seen.add(ref)
            if not (graph.root / ref).exists():
                missing.append((ref, path, line))
    rows += ["", f"distinct tools/ paths mentioned in live docs: {len(seen)}   "
                 f"documented but missing on disk: {len(missing)}",
             "scope: dated records excluded (" + ", ".join(sorted(HISTORICAL)) + ")"]
    for ref, path, line in missing[:MAX_ROWS]:
        rows.append(f"  MISSING  {ref}   (documented at {path}:{line})")

    env = graph.read(".agents/Environment.md")
    rows += ["", "toolchain coverage in .agents/Environment.md:"]
    for tool in TOOLCHAIN:
        rows.append(f"  {tool:<16} {'recorded' if tool in env else 'NOT recorded'}")
    return "toolchain audit: gate wiring, documented commands, install paths", rows


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
