#!/usr/bin/env python3
"""web-spec-conformance — repository code graph plus the constant/pin audit.

Remit: implementation versus published specification, both sides cited.
Read-only: writes only the report path given with `--json`.

    python3 .subagents/web-spec-conformance/codegraph.py --json reports/latest.json
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

SUB = "web-spec-conformance"
KIND = "web-research"
REMIT = ("Cross-check implemented format constants, magic numbers, pinned "
         "revisions and version literals against the specification and the "
         "in-tree docs.")
FOCUS = [
    "include/*.h", "src/*.c", "src/*.h", "android/app/src/main/cpp/*.c",
    "android/app/src/main/cpp/*.h", "tools/gguf_*.py", "tools/make_model.py",
    "docs/FORMAT*.md", "docs/GGUF-IMPORT.md", "docs/ARCHITECTURE.md",
]
HEX_RE = r"\b0x[0-9A-Fa-f]{6,}\b"
SHA_RE = r"\b[0-9a-f]{40}\b"
VERSION_RE = r"\b(?:VERSION|version|FORMAT_VERSION)\b\s*(?:=|:)\s*[0-9]+"
MAX_ROWS = 24


def _load_core():
    here = Path(__file__).resolve()
    root = here.parents[2]
    sys.path.insert(0, str(root / ".subagents" / "tools"))
    import codegraph_core as core  # noqa: E402

    core.repo_root_from(__file__, 2)
    return here, root, core


def extra(graph, core):
    impl = [n for n in graph.match(["include/", "src/",
                                   "android/app/src/main/cpp/", "tools/"])
            if n.kind == "code"]
    # The specification side is the project's docs, NOT this team's own output:
    # the first version counted `.subagents/*/PROPOSALS.md` as documentation, so
    # every constant it listed became "documented" by the act of reporting it
    # (found 2026-10-29; kept as a symptom).
    spec_docs = [n for n in graph.docs() if not n.path.startswith(".subagents/")]
    docs_text = "\n".join(graph.read(n) for n in spec_docs).lower()
    rows = []

    hexes = core.find_pattern(graph, impl, HEX_RE, max_hits=120)
    rows.append(f"hex constants of 6+ digits in implementation files: {len(hexes)} lines")
    for path, line, text in hexes[:MAX_ROWS]:
        for value in re.findall(HEX_RE, text):
            dec = str(int(value, 16))
            documented = (value.lower() in docs_text or value[2:].lower() in docs_text
                          or dec in docs_text)
            rows.append(f"  {value:<12} {path}:{line}  "
                        f"{'documented' if documented else 'NOT in any .md - classify (wire value or internal detail)'}")
    if len(hexes) > MAX_ROWS:
        rows.append(f"  ... {len(hexes) - MAX_ROWS} more lines")

    by_sha = defaultdict(list)
    for path, line, text in core.find_pattern(graph, graph.text_nodes(), SHA_RE, max_hits=80):
        for value in re.findall(SHA_RE, text):
            by_sha[value].append(f"{path}:{line}")
    rows += ["", f"pinned 40-hex revisions: {len(by_sha)} distinct value(s)"]
    for value in sorted(by_sha):
        places = by_sha[value]
        rows.append(f"  {value[:12]}...  mentioned {len(places)}x")
        for place in places[:6]:
            rows.append(f"      {place}")
        if len(places) > 6:
            rows.append(f"      ... {len(places) - 6} more")

    versions = core.find_pattern(graph, impl, VERSION_RE, max_hits=40)
    rows += ["", f"version literals in implementation: {len(versions)}"]
    for path, line, text in versions[:MAX_ROWS]:
        rows.append(f"  {path}:{line}  {text}")
    return "spec cross-check: constants, pins, version literals", rows


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
