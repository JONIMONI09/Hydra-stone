#!/usr/bin/env python3
"""Run the whole `.subagents` team and keep the receipts.

WHAT IT DOES
    For every sub-agent folder it executes that folder's own `codegraph.py`,
    captures the full output into `reports/latest.txt`, keeps the JSON report the
    script writes (`reports/latest.json`), and prints one summary row per
    sub-agent: exit code, file count, Markdown count and open work items.

WHY IT EXISTS
    The owner's rule for this team is "no fake data, show the evidence". A
    sub-agent that is described in prose but never executed is a claim without a
    proof, so this runner produces the proof and stores it next to the sub.

FAILURE HANDLING (owner: "wenn ein Sub ausfällt ihn wiederholen")
    A failing sub-agent is retried once; both attempts are recorded in the text
    report and in the console summary. A sub-agent that fails twice makes the
    whole run exit non-zero - a silent failure would be worse than none.

Usage
    python3 .subagents/tools/run_all.py            # run all seven
    python3 .subagents/tools/run_all.py --only critic-final
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path

TEAM = (
    "web-source-verifier",
    "web-spec-conformance",
    "web-tooling-scout",
    "critic-evidence",
    "critic-architecture",
    "critic-final",
    "ai-threat-scan",
)
MAX_ATTEMPTS = 2


def _load_module(script: Path, name: str):
    spec = importlib.util.spec_from_file_location(f"subagents_{name.replace('-', '_')}", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_one(root: Path, sub: str) -> dict:
    folder = root / ".subagents" / sub
    script = folder / "codegraph.py"
    reports = folder / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    attempts, output, last_error = [], "", ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        buffer = io.StringIO()
        try:
            module = _load_module(script, sub)
            with contextlib.redirect_stdout(buffer):
                code = module.main(["--json", "reports/latest.json"])
            text = buffer.getvalue()
        except Exception as exc:  # noqa: BLE001 - a sub-agent failure must be reported, not hidden
            code = 1
            text = buffer.getvalue() + f"\n[run_all] {type(exc).__name__}: {exc}\n"
            last_error = f"{type(exc).__name__}: {exc}"
        attempts.append((attempt, code))
        output = text
        if code == 0:
            break
        print(f"  attempt {attempt} failed for {sub} (rc={code}); retrying"
              if attempt < MAX_ATTEMPTS else
              f"  attempt {attempt} failed for {sub} (rc={code}); giving up")

    header = (f"# {sub} - codegraph run\n"
              f"# attempts: {attempts}\n"
              f"# exit code: {attempts[-1][1]}\n"
              f"{'# error: ' + last_error if last_error else ''}\n"
              + "-" * 78 + "\n")
    (reports / "latest.txt").write_text(header + output, encoding="utf-8")

    stats = {}
    payload_path = reports / "latest.json"
    if payload_path.is_file():
        try:
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            stats = payload.get("stats", {})
            check = (payload.get("extra") or {}).get("check", "")
        except ValueError:
            check = "report not parseable"
    else:
        check = "no json report"
    return {
        "sub": sub,
        "rc": attempts[-1][1],
        "attempts": len(attempts),
        "files": stats.get("files", 0),
        "docs": stats.get("docs", 0),
        "open_items": stats.get("open_items", 0),
        "markers": stats.get("markers", 0),
        "check": check,
        "error": last_error,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run every .subagents sub-agent.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--only", action="append", choices=TEAM,
                        help="run only the named sub-agent (repeatable)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    selected = args.only or list(TEAM)
    rows = []
    for sub in selected:
        print(f"[{sub}]")
        rows.append(run_one(root, sub))

    print("")
    print(f"{'sub-agent':<22} {'rc':>3} {'try':>4} {'files':>6} {'md':>4} "
          f"{'open':>5} {'markers':>8}  check")
    print("-" * 110)
    for row in rows:
        print(f"{row['sub']:<22} {row['rc']:>3} {row['attempts']:>4} {row['files']:>6} "
              f"{row['docs']:>4} {row['open_items']:>5} {row['markers']:>8}  {row['check']}")
    failed = [row for row in rows if row["rc"] != 0]
    print("")
    if failed:
        print(f"RUN-ALL: FAIL - {len(failed)} sub-agent(s) failed twice: "
              + ", ".join(row["sub"] for row in failed))
        return 1
    print(f"RUN-ALL: ok - {len(rows)} sub-agent(s) ran, reports in "
          f".subagents/*/reports/latest.{{txt,json}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
