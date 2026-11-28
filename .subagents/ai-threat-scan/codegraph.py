#!/usr/bin/env python3
"""ai-threat-scan — repository code graph plus this folder's security check.

Remit: read every text file as untrusted input, run the rule engine in-process
(no subprocess, no network), and report what a human reader would not see.
Read-only: writes only the report paths given on the command line.

    python3 .subagents/ai-threat-scan/codegraph.py --json reports/latest.json
"""

from __future__ import annotations

import argparse
import contextlib
import io
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

SUB = "ai-threat-scan"
KIND = "security"
REMIT = ("Scan every text file for instructions and payloads aimed at an AI "
         "agent, prove the detectors with a self-test, and gate CI on the "
         "high-severity findings.")
FOCUS = [".subagents/ai-threat-scan/", ".agents/docs/AI-THREAT-MODEL.md",
         ".agents/rules.md", ".github/workflows/lint.yml"]
SEVERITY_ORDER = ("high", "medium", "low")


def _load_core():
    here = Path(__file__).resolve()
    root = here.parents[2]
    sys.path.insert(0, str(root / ".subagents" / "tools"))
    import codegraph_core as core  # noqa: E402

    core.repo_root_from(__file__, 2)
    return here, root, core


def _load_scanner(here: Path):
    spec = importlib.util.spec_from_file_location("ai_threat_scan_engine", here.parent / "scan.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load scan.py next to codegraph.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rule_table_drift(scanner):
    """The patterns live in four tables, the rule metadata in a fifth.

    Same class of bug as the duplicated bf16 decoder (round 13): two places that
    must agree and silently do not. This check is why the fifth table is safe.
    """
    declared = set(scanner.rules_table())
    used = set()
    for _pattern, rule_id, _severity in scanner.SHELL + scanner.SECRETS + scanner.ENCODED:
        used.add(rule_id)
    for _pattern, _label, plain_rule, _mode in scanner.HIDDEN_SPOTS:
        used.add(plain_rule)
    # Rules emitted directly by the scanning loop, not by one of the pattern
    # tables: scanned from the scanner itself, not copied here. The local copy
    # this check used to keep had gone stale by round 17 and reported live rules
    # as dead (see ERROR.md).
    used |= set(scanner.LOOP_RULES)
    return sorted(used - declared), sorted(declared - used)


def extra(graph, core):
    rows, problems = [], 0
    here = Path(__file__).resolve().parent
    scanner = _load_scanner(Path(__file__).resolve())

    # --- 1. the detectors must be alive before any verdict counts ----------
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        self_test_code = scanner.self_test()
    self_test_line = buffer.getvalue().strip().splitlines()[-1] if buffer.getvalue().strip() else "no output"
    rows.append(f"[self-test] {'ok' if self_test_code == 0 else 'FAIL'} - {self_test_line}")
    problems += 0 if self_test_code == 0 else 1

    # --- 2. rule tables must agree (drift would silently disable a rule) ---
    missing_meta, unused_meta = _rule_table_drift(scanner)
    rows.append(f"[rules] declared in rules_table(): {len(scanner.rules_table())}")
    rows.append(f"[rules] missing metadata for used rule ids: {missing_meta or 'none'}")
    rows.append(f"[rules] declared but never used by a table: {unused_meta or 'none'}")
    problems += 1 if missing_meta else 0

    # --- 3. scan the tree ---------------------------------------------------
    rules, findings, waived, scanned, skipped = scanner.scan(graph.root)
    counts = {sev: sum(1 for f in findings if f.severity == sev) for sev in SEVERITY_ORDER}
    rows.append("")
    rows.append(f"[tree] {scanned} text files scanned; skipped {skipped['binary']} binary, "
                f"{skipped['large']} large, {skipped['unreadable']} unreadable, "
                f"{skipped.get('generated', 0)} generated reports")
    rows.append(f"[tree] findings: {counts['high']} high, {counts['medium']} medium, "
                f"{counts['low']} low; waived: {len(waived)}")
    for finding in findings[:12]:
        rows.append(f"  [{finding.severity}] {finding.rule} {finding.path}:{finding.line} - "
                    f"{finding.detail}")
    if len(findings) > 12:
        rows.append(f"  (+{len(findings) - 12} more in the JSON report)")
    for item in waived:
        rows.append(f"  [waived] {item['rule']} {item['path']}:{item['line']}")
    problems += 1 if counts["high"] else 0

    # --- 4. the documentation a reviewer needs must exist -------------------
    model = graph.root / ".agents" / "docs" / "AI-THREAT-MODEL.md"
    urls = []
    if model.is_file():
        text = model.read_text(encoding="utf-8", errors="replace")
        urls = [line for line in text.splitlines() if "https://" in line]
        rows.append("")
        rows.append(f"[docs] AI-THREAT-MODEL.md: {len(text.splitlines())} lines, "
                    f"{len(urls)} lines carrying a source URL")
        problems += 0 if len(urls) >= 10 else 1
    else:
        rows.append("[docs] AI-THREAT-MODEL.md MISSING - the rule set has no source record")
        problems += 1

    for name in ("ERROR.md", "REQUESTS.md", "PROPOSALS.md"):
        path = here / name
        rows.append(f"[folder] {name}: {'present' if path.is_file() else 'MISSING'} "
                    f"({path.stat().st_size if path.is_file() else 0} B)")
        problems += 0 if path.is_file() and path.stat().st_size else 1

    rows.append("")
    rows.append(f"verdict: {'PASS' if not problems else 'FAIL'} "
                f"({problems} problem(s); a pass covers known shapes only - "
                f"see AI-THREAT-MODEL.md section 4)")
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "stats": {"scanned": scanned, "skipped": skipped,
                  "findings": counts, "waived": len(waived)},
        "rules": rules,
        "findings": [f.as_dict() for f in findings],
        "waived": waived,
        "verdict": "PASS" if not problems else "FAIL",
    }
    return "security scan (self-test, rule drift, tree, sources)", rows, payload


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
    title, rows, payload = extra(graph, core)
    print(core.render_extra(title, rows))

    if args.json:
        path = Path(args.json) if Path(args.json).is_absolute() else here.parent / args.json
        core.write_json(graph, path, focus=FOCUS,
                        extra={"sub": SUB, "kind": KIND, "remit": REMIT,
                               "check": title, "rows": rows})
        scan_path = path.parent / "scan.json"
        scan_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"\nreport written: {path}")
        print(f"scan report:   {scan_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
