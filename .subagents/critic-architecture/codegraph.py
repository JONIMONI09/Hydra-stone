#!/usr/bin/env python3
"""critic-architecture — repository code graph plus the structure audit.

Remit: duplicate implementations, dead header declarations, oversized units.
Read-only: writes only the report path given with `--json`.

    python3 .subagents/critic-architecture/codegraph.py --json reports/latest.json
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SUB = "critic-architecture"
KIND = "critic"
REMIT = ("Judge structure: duplicate implementations, declarations nobody uses, "
         "and rules that live in two places instead of one.")
FOCUS = ["src/", "include/", "tests/", "tools/", "server.js", "android/app/src/main/cpp/",
         ".subagents/*/PROPOSALS.md"]
PROTO_RE = re.compile(r"\b([a-z_][a-z0-9_]{4,})\s*\(")
MAX_ROWS = 14


def _load_core():
    here = Path(__file__).resolve()
    root = here.parents[2]
    sys.path.insert(0, str(root / ".subagents" / "tools"))
    import codegraph_core as core  # noqa: E402

    core.repo_root_from(__file__, 2)
    return here, root, core


def extra(graph, core):
    rows = []

    mentioned = {}
    for node in graph.code():
        if node.ext == ".h":
            continue
        for name in PROTO_RE.findall(graph.read(node)):
            mentioned[name] = mentioned.get(name, 0) + 1

    declared, unused = 0, []
    for node in graph.match(["include/"]):
        if node.ext != ".h":
            continue
        # `foo_t` is a typedef by convention, not a function declaration; the
        # first run filed `hydra_kv_cache_t` as a dead function (kept as a
        # symptom of the naive pattern).
        names = sorted({n for n in PROTO_RE.findall(graph.read(node))
                        if n.startswith(("hydra_", "hydra2_"))
                        and not n.endswith("_t")})
        declared += len(names)
        for name in names:
            if not mentioned.get(name):
                unused.append((node.path, name))

    rows.append(f"public declarations in include/ (hydra_*, hydra2_*): {declared}")
    rows.append(f"declared but mentioned in no C/Kotlin source: {len(unused)}")
    rows.append("  (check the JNI bridge before filing: a function called only")
    rows.append("   through System.loadLibrary / llama_jni is not dead)")
    for path, name in unused[:MAX_ROWS]:
        rows.append(f"  [dead?] {name:<34} declared at {path}")
    if len(unused) > MAX_ROWS:
        rows.append(f"  ... {len(unused) - MAX_ROWS} more")

    dups = core.duplicate_definitions(graph)
    rows += ["", f"names defined in more than one source file (heuristic): {len(dups)}"]
    for name in sorted(dups):
        places = dups[name][:4]
        rows.append(f"  [dup] {name:<30} {len(dups[name])} files")
        for place in places:
            rows.append(f"        {place}")
    if not dups:
        rows.append("  (none found)")

    largest = sorted(graph.code(), key=lambda n: -n.lines)[:8]
    rows += ["", "largest units by line count (context, not a defect):"]
    for node in largest:
        rows.append(f"  {node.lines:>6} lines  {node.size:>8} B  {node.path}")
    return "structure audit: duplicates, dead declarations, largest units", rows


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
