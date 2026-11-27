#!/usr/bin/env python3
"""web-source-verifier — repository code graph plus the source census.

Remit: verify every externally sourced fact against a primary source.
Read-only: the only file written is the report path given with `--json`.

    python3 .subagents/web-source-verifier/codegraph.py --json reports/latest.json
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

SUB = "web-source-verifier"
KIND = "web-research"
REMIT = ("Verify every externally sourced fact (versions, API behaviour, format "
         "constants, tool flags, security ids) against its primary source and "
         "cite the URL that was read.")
FOCUS = [
    "README.md", "AGENTS.md", "CHANGELOG.md", "CLAUDE.md",
    "docs/*.md", ".agents/*.md", ".agents/docs/*.md", ".agents/skills/*/SKILL.md",
]

# A host is PRIMARY when it is the upstream project, the vendor or the standards
# body itself. Anything else is flagged for a human look: a blog can be right,
# but it cannot be the proof (R26).
PRIMARY_HOSTS = (
    "github.com/ggml-org", "ggml.ai", "adk.dev", "ai.google.dev",
    "developer.android.com", "kotlinlang.org", "docs.python.org", "nodejs.org",
    "pypi.org", "npmjs.com", "kernel.org", "w3.org", "rfc-editor.org",
    "llvm.org", "gcc.gnu.org", "nvd.nist.gov", "cwe.mitre.org", "man7.org",
)
# A pin is a version token (`v1.2.3`), the word "pinned", or a hex revision
# (7-40 hex chars containing at least one letter AND one digit, so plain numbers
# such as a workflow id or a PR number are not mistaken for a commit id).
# A pin is a version token (`v1.2.3`), the word "pinned", or a free-standing hex
# revision. The lookarounds matter: a revision glued into a larger identifier
# (branch `arena/ed8432d1-bestai`) is an internal name, not a source claim.
PIN_RE = (r"\bv\d+\.\d+(?:\.\d+)?\b|\bpinned\b|"
          r"(?<![0-9a-z/_-])(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)"
          r"[0-9a-f]{7,40}(?![0-9a-z_-])")
URL_IN_LINE = ("http://", "https://")
MAX_ROWS = 18

# Two further classes, because "not primary" is not the same as "bad source":
# a code host serves whatever the owner uploaded, so the ORG has to match the
# upstream project; a peer-reviewed preprint is good context but never the
# proof of an API's behaviour.
CODE_HOSTS = ("github.com", "codeload.github.com", "raw.githubusercontent.com",
              "dl.google.com", "services.gradle.org", "repo1.maven.org",
              "registry.npmjs.org", "files.pythonhosted.org")
SECONDARY_HOSTS = ("arxiv.org", "stackoverflow.com", "medium.com", "dev.to",
                   "reddit.com", "news.ycombinator.com")


def _load_core():
    here = Path(__file__).resolve()
    root = here.parents[2]
    sys.path.insert(0, str(root / ".subagents" / "tools"))
    import codegraph_core as core  # noqa: E402  (path set up above)

    core.repo_root_from(__file__, 2)
    return here, root, core


def _is_primary(host: str) -> bool:
    return any(host == h or host.endswith("." + h) for h in PRIMARY_HOSTS)


def _classify(host: str) -> str:
    if _is_primary(host):
        return "primary"
    if any(host == h or host.endswith("." + h) for h in CODE_HOSTS):
        return "vendor/code host - verify the org is the upstream project"
    if any(host == h or host.endswith("." + h) for h in SECONDARY_HOSTS):
        return "secondary - context only, never the proof"
    if host.startswith("localhost") or host.startswith("127.0.0.1"):
        return "local run artefact"
    return "CHECK - not a known primary source"


def extra(graph, core):
    docs = [n for n in graph.match(FOCUS) if n.kind == "doc"] or graph.docs()
    urls = core.extract_urls(graph, docs)
    hosts = Counter(urlparse(url).netloc for _, _, url in urls)
    docs_without_urls = [n.path for n in docs if not any(p == n.path for p, _, _ in urls)]

    rows = [f"documents scanned: {len(docs)}   URLs found: {len(urls)}", "",
            "host census (count, host, source class):"]
    for host, count in hosts.most_common(12):
        rows.append(f"  {count:>4}  {host:<40} {_classify(host)}")

    # Verdicts are per DOCUMENT, not per line: a source URL is often cited in
    # the next line, so a line-local test produced 259 false queue entries when
    # it was first written (documented in PROPOSALS.md, kept as a symptom).
    pin_hits = {}
    for path, line, text in core.find_pattern(graph, docs, PIN_RE, max_hits=4000):
        pin_hits.setdefault(path, []).append((line, text))
    unsourced = [n.path for n in docs
                 if pin_hits.get(n.path) and not any(p == n.path for p, _, _ in urls)]
    rows += ["", f"documents that state a version/pin: {len(pin_hits)}",
             f"...of those, documents with NO source URL anywhere: {len(unsourced)}"]
    for path in unsourced[:MAX_ROWS]:
        sample = pin_hits[path][:2]
        rows.append(f"  {path}  ({len(pin_hits[path])} pin line(s))")
        for line, text in sample:
            rows.append(f"      :{line}  {text}")
    if len(unsourced) > MAX_ROWS:
        rows.append(f"  ... {len(unsourced) - MAX_ROWS} more")

    rows += ["", f"documents with no external URL at all: {len(docs_without_urls)}"]
    for path in docs_without_urls[:MAX_ROWS]:
        rows.append(f"  {path}")
    if len(docs_without_urls) > MAX_ROWS:
        rows.append(f"  ... {len(docs_without_urls) - MAX_ROWS} more")
    return "source census: hosts, and pin/version claims without a source", rows


def main(argv=None) -> int:
    here, root, core = _load_core()
    parser = argparse.ArgumentParser(prog=f"{SUB}/codegraph.py", description=REMIT)
    parser.add_argument("--json", metavar="PATH",
                        help="write the machine-readable report here (relative to this folder)")
    parser.add_argument("--md-only", action="store_true", help="hide the code/edge sections")
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
