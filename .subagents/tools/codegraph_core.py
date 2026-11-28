#!/usr/bin/env python3
"""Repository code graph for the `.subagents` team.

WHY THIS EXISTS
    Every sub-agent needs the same ground truth before it may say anything
    about the repository: which files exist, how old they are, which docs
    exist, how the files depend on each other, and which written-down work
    items are still open. The owner's standing rules for the sub-agents are
    "no guessing" and "no fake data", so the graph is built by walking the
    tree with the standard library only and by reading the files. There is
    no hard-coded file list and no sample output anywhere in this module.

WHAT IT REPORTS
    * every file: size, mtime (the "Aenderungsdatum" the owner asked for),
      line count for text files, language guess, first path segment
    * every Markdown file, newest first, plus a doc-lag signal when a doc is
      older than the newest source file of the area it documents
    * internal dependency edges (`#include "..."`, Python imports, JS
      require/import, Kotlin imports, shell `bash tools/...` calls) and the
      external names that could not be resolved inside the tree
    * written-down open work: `- [ ]` checkboxes in Markdown, and
      TODO/FIXME/XXX/HACK/PLACEHOLDER markers in source
    * a focus view per sub-agent (its own globs) so each sub sees its remit

WHAT IT DOES NOT DO
    * it never writes to the repository except the JSON report a caller
      explicitly asks for with `--json <path>`
    * it does not run git, a compiler or a network call (a sub-agent's
      report must stay reproducible in a sandbox without those)

Usage from a sub-agent folder is a thin, real wrapper: see
`.subagents/<name>/codegraph.py`, which supplies that sub's profile and one
extra check of its own.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Directories that are not part of this project's own source: VCS data,
# installed dependencies, build output, and the pinned llama.cpp submodule
# (upstream code, never edited here — see .agents/skills/repo-docs-audit).
DEFAULT_EXCLUDES = (
    ".git",
    "node_modules",
    "__pycache__",
    ".gradle",
    ".idea",
    ".vscode",
    "build",
    "dist",
    "llama.cpp",
    "android/app/src/main/cpp/llama",
    # Generated receipts. Scanning them fed each run's own marker list back into
    # the next run: the marker count jumped from 8 to 19,220 after the first
    # team run (kept as a symptom; the reports are derived artefacts, not
    # source).
    ".subagents/*/reports",
)

TEXT_EXTENSIONS = {
    ".c", ".h", ".cpp", ".hpp", ".cc", ".kt", ".java", ".py", ".js", ".mjs",
    ".sh", ".bash", ".md", ".txt", ".json", ".yml", ".yaml", ".toml", ".cfg",
    ".gradle", ".xml", ".html", ".css", ".properties", ".mk", ".gitignore",
    ".gitmodules", ".pro", ".smk",
}

LANG_BY_EXT = {
    ".c": "C", ".h": "C header", ".cpp": "C++", ".cc": "C++", ".hpp": "C++ header",
    ".kt": "Kotlin", ".java": "Java", ".py": "Python", ".js": "JavaScript",
    ".mjs": "JavaScript", ".sh": "Shell", ".bash": "Shell", ".md": "Markdown",
    ".json": "JSON", ".yml": "YAML", ".yaml": "YAML", ".toml": "TOML",
    ".gradle": "Gradle", ".xml": "XML", ".html": "HTML", ".css": "CSS",
}

MAX_TEXT_BYTES = 2 * 1024 * 1024  # a larger "text" file is listed but not scanned

# Marker patterns. The detector sources are skipped when scanning (see
# MARKER_SCAN_SKIP) because a pattern definition matches itself and would
# report a work item that does not exist.
MARKER_RE = re.compile(r"\b(TODO|FIXME|XXX|HACK|PLACEHOLDER)\b")
MARKER_SCAN_SKIP = {
    ".subagents/tools/codegraph_core.py",
    ".subagents/tools/check_subagents.py",
    ".subagents/tools/run_all.py",
}
# A doc-lag delta smaller than this is measurement noise, not staleness: git
# does not preserve mtimes, so a fresh checkout stamps every file within
# seconds of each other. Only a doc that trails its area by a real edit gap is
# reported.
DOC_LAG_MIN_SECONDS = 3600.0
OPEN_ITEM_RE = re.compile(r"^\s*[-*]\s+\[ \]\s+(.*\S)\s*$")
INCLUDE_RE = re.compile(r'^\s*#\s*include\s+"([^"]+)"', re.MULTILINE)
PY_IMPORT_RE = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.MULTILINE)
JS_REQUIRE_RE = re.compile(r"""(?:require\(\s*['"]([^'"]+)['"]|from\s+['"]([^'"]+)['"])""")
KT_IMPORT_RE = re.compile(r"^\s*import\s+([\w.]+)", re.MULTILINE)
SH_CALL_RE = re.compile(r"(?:bash|sh)\s+((?:tools|\.subagents)/[\w./-]+\.(?:sh|py))")


@dataclass
class Node:
    path: str
    size: int
    mtime: float
    ext: str
    kind: str            # "code" | "doc" | "config" | "asset" | "other"
    lang: str
    area: str
    lines: int = 0
    binary: bool = False

    @property
    def stamp(self) -> str:
        return datetime.fromtimestamp(self.mtime).strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Graph:
    root: Path
    generated_at: float
    excluded: tuple
    nodes: list = field(default_factory=list)     # list[Node]
    edges: list = field(default_factory=list)     # list[(src, dst, how)]
    external: list = field(default_factory=list)  # list[(src, name, how)]
    markers: list = field(default_factory=list)   # list[(path, line, kind, text)]
    open_items: list = field(default_factory=list)  # list[(path, line, text)]
    areas: dict = field(default_factory=dict)     # area -> dict
    doc_lag: list = field(default_factory=list)   # list[(doc, area, newest_src, days)]
    truncated: list = field(default_factory=list)  # text files too large to scan

    # -- lookups ---------------------------------------------------------
    def by_path(self) -> dict:
        return {n.path: n for n in self.nodes}

    def docs(self) -> list:
        return sorted((n for n in self.nodes if n.kind == "doc"), key=lambda n: n.path)

    def code(self) -> list:
        return [n for n in self.nodes if n.kind == "code"]

    def match(self, patterns) -> list:
        """Return nodes whose path matches any glob (simple `*` semantics)."""
        out = []
        for n in self.nodes:
            for pat in patterns:
                base = pat.rstrip("*").rstrip("/")
                if fnmatch.fnmatch(n.path, pat) or (base and n.path.startswith(base + "/")):
                    out.append(n)
                    break
        return sorted(out, key=lambda n: n.path)

    def read(self, node_or_path) -> str:
        path = node_or_path.path if isinstance(node_or_path, Node) else node_or_path
        full = self.root / path
        try:
            if full.stat().st_size > MAX_TEXT_BYTES:
                return ""
            return full.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    def text_nodes(self) -> list:
        return [n for n in self.nodes if not n.binary and n.ext in TEXT_EXTENSIONS]


def _kind_for(ext: str, rel: str) -> str:
    if ext == ".md":
        return "doc"
    if ext in {".c", ".h", ".cpp", ".hpp", ".cc", ".kt", ".java", ".py", ".js",
               ".mjs", ".sh", ".bash"}:
        return "code"
    if ext in {".json", ".yml", ".yaml", ".toml", ".gradle", ".mk", ".xml",
               ".cfg", ".properties"} or rel.endswith(("Makefile", ".gitignore",
                                                       ".gitmodules")):
        return "config"
    if ext in {".html", ".css", ".png", ".jpg", ".svg", ".ico"}:
        return "asset"
    return "other"


def _is_excluded(rel: str, exclude) -> bool:
    """True for an exact path, a parent prefix or a glob pattern."""
    for pattern in exclude:
        if rel == pattern or rel.startswith(pattern.rstrip("/") + "/"):
            return True
        if fnmatch.fnmatch(rel, pattern):
            return True
    return False


def _is_binary(full: Path) -> bool:
    try:
        with open(full, "rb") as fh:
            return b"\0" in fh.read(4096)
    except OSError:
        return True


def build_graph(root: Path, exclude=DEFAULT_EXCLUDES) -> Graph:
    """Walk the repository and build the full graph. Read-only."""
    root = Path(root).resolve()
    g = Graph(root=root, generated_at=datetime.now().timestamp(), excluded=tuple(exclude))
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root).replace(os.sep, "/")
        if rel_dir == ".":
            rel_dir = ""
        dirnames[:] = sorted(
            d for d in dirnames
            if d != ".git" and not _is_excluded(f"{rel_dir}/{d}".lstrip("/"), exclude)
        )
        for name in sorted(filenames):
            rel = f"{rel_dir}/{name}".lstrip("/")
            if _is_excluded(rel, exclude):
                continue
            full = Path(dirpath) / name
            try:
                st = full.stat()
            except OSError:
                continue
            ext = Path(name).suffix.lower()
            binary = ext not in TEXT_EXTENSIONS and ext != ""
            if ext == "":
                binary = _is_binary(full)
            lines = 0
            if not binary:
                if st.st_size > MAX_TEXT_BYTES:
                    g.truncated.append(rel)
                else:
                    try:
                        with open(full, "r", encoding="utf-8", errors="replace") as fh:
                            lines = sum(1 for _ in fh)
                    except OSError:
                        lines = 0
            area = rel.split("/")[0] if "/" in rel else "(root)"
            g.nodes.append(Node(path=rel, size=st.st_size, mtime=st.st_mtime, ext=ext,
                                kind=_kind_for(ext, rel), lang=LANG_BY_EXT.get(ext, "other"),
                                area=area, lines=lines, binary=binary))

    _build_edges(g)
    _scan_markers(g)
    _scan_open_items(g)
    _compute_areas(g)
    _compute_doc_lag(g)
    return g


# -- edges -----------------------------------------------------------------
def _resolve(g: Graph, src: Node, raw: str, how: str, index: dict) -> None:
    raw = raw.strip()
    if not raw:
        return
    candidates = []
    if how == "include":
        candidates = [f"include/{raw}", f"src/{raw}", f"tests/{raw}",
                      str(Path(src.path).parent / raw)]
    elif how == "python":
        dotted = raw.replace("/", ".")
        base = dotted.replace(".", "/")
        candidates = [f"{base}.py", f"{base}/__init__.py",
                      f"tools/{base}.py", f"{base.rsplit('/', 1)[-1]}.py"]
    elif how in {"js", "shell"}:
        if raw.startswith("."):
            candidates = [os.path.normpath(str(Path(src.path).parent / raw)).replace(os.sep, "/")]
        else:
            base = raw
            candidates = [base, f"{base}.js", f"{base}.py", f"{base}.sh",
                          f"public/{base}", f"public/{base}.js"]
    elif how == "kotlin":
        tail = raw.split(".")[-1]
        candidates = [n.path for n in g.nodes
                      if n.path.endswith(f"/{tail}.kt") or n.path.endswith(f"/{tail}.java")]
    for cand in candidates:
        cand = cand.replace(os.sep, "/").lstrip("./")
        if cand in index:
            g.edges.append((src.path, cand, how))
            return
    g.external.append((src.path, raw, how))


def _build_edges(g: Graph) -> None:
    index = g.by_path()
    for n in g.nodes:
        if n.binary or n.size > MAX_TEXT_BYTES:
            continue
        text = g.read(n)
        if not text:
            continue
        if n.ext in {".c", ".h", ".cpp", ".hpp", ".cc"}:
            for raw in INCLUDE_RE.findall(text):
                _resolve(g, n, raw, "include", index)
        elif n.ext == ".py":
            for a, b in PY_IMPORT_RE.findall(text):
                _resolve(g, n, a or b, "python", index)
        elif n.ext in {".js", ".mjs"}:
            for a, b in JS_REQUIRE_RE.findall(text):
                _resolve(g, n, a or b, "js", index)
        elif n.ext in {".kt", ".java"}:
            for raw in KT_IMPORT_RE.findall(text):
                if raw.startswith("dev.hydrastone") or raw.startswith("java.") is False:
                    _resolve(g, n, raw, "kotlin", index)
        elif n.ext in {".sh", ".bash", ".md", ".yml", ".yaml"}:
            for raw in SH_CALL_RE.findall(text):
                _resolve(g, n, raw, "shell", index)
    g.edges.sort()
    g.external.sort()


# -- signals ---------------------------------------------------------------
def _scan_markers(g: Graph) -> None:
    # Source comments only. Markdown legitimately DISCUSSES these markers (this
    # repository's own docs do), so scanning prose would report a work item that
    # does not exist; written-down work in Markdown is the checkbox scan below.
    for n in g.nodes:
        if n.binary or n.kind == "doc" or n.path in MARKER_SCAN_SKIP \
                or n.size > MAX_TEXT_BYTES:
            continue
        text = g.read(n)
        if not text:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            m = MARKER_RE.search(line)
            if m:
                g.markers.append((n.path, i, m.group(1), line.strip()[:160]))


def _scan_open_items(g: Graph) -> None:
    for n in g.nodes:
        if n.kind != "doc" or n.size > MAX_TEXT_BYTES:
            continue
        text = g.read(n)
        for i, line in enumerate(text.splitlines(), 1):
            m = OPEN_ITEM_RE.match(line)
            if m:
                g.open_items.append((n.path, i, m.group(1)[:200]))


def _compute_areas(g: Graph) -> None:
    for n in g.nodes:
        area = g.areas.setdefault(n.area, {
            "files": 0, "bytes": 0, "code": 0, "docs": 0,
            "newest": 0.0, "newest_path": "", "newest_code": 0.0, "newest_code_path": "",
        })
        area["files"] += 1
        area["bytes"] += n.size
        if n.kind == "code":
            area["code"] += 1
        if n.kind == "doc":
            area["docs"] += 1
        if n.mtime > area["newest"]:
            area["newest"] = n.mtime
            area["newest_path"] = n.path
        if n.kind in {"code", "config"} and n.mtime > area["newest_code"]:
            area["newest_code"] = n.mtime
            area["newest_code_path"] = n.path


def _compute_doc_lag(g: Graph) -> None:
    """A doc older than the newest source of its area may be out of date."""
    for doc in g.docs():
        area = g.areas.get(doc.area)
        if not area or not area["newest_code"]:
            continue
        delta = area["newest_code"] - doc.mtime
        if delta >= DOC_LAG_MIN_SECONDS:
            g.doc_lag.append((doc.path, doc.area, area["newest_code_path"],
                              delta / 86400.0))
    g.doc_lag.sort(key=lambda t: -t[3])


# -- shared helpers for the sub-agent profiles -----------------------------
def extract_urls(g: Graph, nodes=None) -> list:
    """Every http(s) URL in the given (default: Markdown) files, with location."""
    found = []
    for n in (nodes if nodes is not None else g.docs()):
        text = g.read(n)
        for i, line in enumerate(text.splitlines(), 1):
            for url in re.findall(r"https?://[^\s)>\]]+", line):
                # Trailing punctuation and Markdown/quote delimiters are not
                # part of the URL; without this the host census fills up with
                # entries like "localhost:8787`".
                found.append((n.path, i, url.rstrip(".,;:`'\"")))
    return found


def find_pattern(g: Graph, nodes, pattern: str, flags=0, max_hits=500) -> list:
    rx = re.compile(pattern, flags)
    hits = []
    for n in nodes:
        if n.binary or n.size > MAX_TEXT_BYTES:
            continue
        for i, line in enumerate(g.read(n).splitlines(), 1):
            if rx.search(line):
                hits.append((n.path, i, line.strip()[:200]))
                if len(hits) >= max_hits:
                    return hits
    return hits


def duplicate_definitions(g: Graph) -> dict:
    """Function-like names defined in more than one source file (R12 smell)."""
    defs = {}
    rx = re.compile(r"^(?:[A-Za-z_][\w\s\*]*?\s+)?([a-z_][a-z0-9_]{4,})\s*\(", re.MULTILINE)
    for n in g.code():
        if n.ext not in {".c", ".h", ".py", ".js", ".kt"}:
            continue
        for name in set(rx.findall(g.read(n))):
            if name in {"if", "for", "while", "switch", "return", "sizeof"}:
                continue
            defs.setdefault(name, set()).add(n.path)
    return {name: sorted(paths) for name, paths in defs.items() if len(paths) > 1}


def gate_wiring(g: Graph) -> list:
    """Which tools/*.sh gates are referenced by a workflow file (real parse)."""
    workflows = [n for n in g.nodes if n.path.startswith(".github/workflows/")]
    wf_text = "\n".join(g.read(n) for n in workflows)
    rows = []
    for n in sorted((x for x in g.nodes if x.path.startswith("tools/") and x.ext == ".sh"),
                    key=lambda x: x.path):
        rows.append((n.path, Path(n.path).name in wf_text))
    return rows


# -- rendering -------------------------------------------------------------
def _human_bytes(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            return f"{value:,.0f} {unit}" if unit == "B" else f"{value:,.1f} {unit}"
        value /= 1024
    return f"{size} B"


def render_text(g: Graph, focus=(), top: int = 25, md_only: bool = False,
                show_edges: bool = True) -> str:
    out = []
    add = out.append
    total = sum(n.size for n in g.nodes)
    text_n = sum(1 for n in g.nodes if not n.binary)
    add("=" * 78)
    add(f"CODE GRAPH — {g.root.name}")
    add(f"generated   {datetime.fromtimestamp(g.generated_at).strftime('%Y-%m-%d %H:%M:%S')}")
    add(f"inventory   {len(g.nodes)} files ({text_n} text, {len(g.nodes) - text_n} binary), "
        f"{_human_bytes(total)}")
    add(f"excluded    {', '.join(g.excluded)}")
    add("=" * 78)

    add("")
    add(f"-- areas ({len(g.areas)}) " + "-" * 50)
    for name in sorted(g.areas):
        a = g.areas[name]
        newest = (datetime.fromtimestamp(a["newest"]).strftime("%Y-%m-%d %H:%M")
                  if a["newest"] else "-")
        add(f"  {name:<28} {a['files']:>4} files  {a['code']:>3} code  {a['docs']:>2} md  "
            f"newest {newest}  {a['newest_path']}")

    add("")
    add(f"-- Markdown inventory ({len(g.docs())}) " + "-" * 40)
    for n in sorted(g.docs(), key=lambda x: (-x.mtime, x.path)):
        add(f"  {n.stamp}  {n.size:>8}  {n.lines:>6} lines  {n.path}")

    if not md_only:
        add("")
        add(f"-- code files newest first ({len(g.code())}) " + "-" * 32)
        for n in sorted(g.code(), key=lambda x: (-x.mtime, x.path))[:top]:
            add(f"  {n.stamp}  {n.size:>8}  {n.path}")

        if show_edges:
            add("")
            add(f"-- internal dependency edges ({len(g.edges)}) " + "-" * 33)
            for src, dst, how in g.edges[:top * 2]:
                add(f"  {src}  ->  {dst}   [{how}]")
            if len(g.edges) > top * 2:
                add(f"  ... {len(g.edges) - top * 2} more (use --json for the full set)")
            add("")
            add(f"-- unresolved (external) references ({len(g.external)}) " + "-" * 24)
            seen = set()
            for src, name, how in g.external:
                key = (name, how)
                if key in seen:
                    continue
                seen.add(key)
                add(f"  {name:<40} [{how}] first seen in {src}")
            if not seen:
                add("  (none)")

    add("")
    add("-- what still needs changing (measured signals) " + "-" * 28)
    add(f"  open checkboxes (written-down work): {len(g.open_items)}")
    for path, line, text in g.open_items[:top]:
        add(f"    [open]   {path}:{line}  {text}")
    if len(g.open_items) > top:
        add(f"    ... {len(g.open_items) - top} more")
    add(f"  marker comments (TODO/FIXME/...): {len(g.markers)}")
    for path, line, kind, text in g.markers[:top]:
        add(f"    [{kind:<11}] {path}:{line}  {text}")
    if len(g.markers) > top:
        add(f"    ... {len(g.markers) - top} more")
    add(f"  docs older than their area's newest source: {len(g.doc_lag)}")
    for doc, area, newest, days in g.doc_lag[:top]:
        add(f"    [doc-lag] {doc}  ({days:.1f} d behind {newest} in {area})")
    if len(g.doc_lag) > top:
        add(f"    ... {len(g.doc_lag) - top} more")
    if g.truncated:
        add(f"  not scanned (> {_human_bytes(MAX_TEXT_BYTES)}): {len(g.truncated)}")
        for path in g.truncated[:5]:
            add(f"    {path}")

    if focus:
        add("")
        add(f"-- focus ({len(g.match(focus))} files) " + "-" * 43)
        for pat in focus:
            hits = g.match([pat])
            add(f"  {pat:<34} {len(hits):>4} files")
            for n in sorted(hits, key=lambda x: (-x.mtime, x.path))[:8]:
                add(f"      {n.stamp}  {n.size:>8}  {n.path}")
            if len(hits) > 8:
                add(f"      ... {len(hits) - 8} more")
    return "\n".join(out)


def render_extra(title: str, rows, empty: str = "  (none found)") -> str:
    out = ["", f"-- {title} " + "-" * max(1, 66 - len(title)), ]
    if not rows:
        out.append(empty)
    for row in rows:
        out.append("  " + (row if isinstance(row, str) else "  ".join(str(x) for x in row)))
    return "\n".join(out)


def to_dict(g: Graph, focus=()) -> dict:
    return {
        "generated_at": datetime.fromtimestamp(g.generated_at).isoformat(timespec="seconds"),
        "root": str(g.root),
        "excluded": list(g.excluded),
        "stats": {
            "files": len(g.nodes),
            "bytes": sum(n.size for n in g.nodes),
            "code": len(g.code()),
            "docs": len(g.docs()),
            "edges": len(g.edges),
            "external": len(g.external),
            "markers": len(g.markers),
            "open_items": len(g.open_items),
            "doc_lag": len(g.doc_lag),
        },
        "nodes": [
            {"path": n.path, "size": n.size, "mtime": n.stamp, "kind": n.kind,
             "lang": n.lang, "area": n.area, "lines": n.lines}
            for n in sorted(g.nodes, key=lambda x: x.path)
        ],
        "edges": [{"from": s, "to": d, "how": h} for s, d, h in g.edges],
        "external": [{"from": s, "name": n, "how": h} for s, n, h in g.external],
        "markers": [{"path": p, "line": l, "kind": k, "text": t} for p, l, k, t in g.markers],
        "open_items": [{"path": p, "line": l, "text": t} for p, l, t in g.open_items],
        "areas": {
            name: {
                "files": a["files"], "bytes": a["bytes"], "code": a["code"],
                "docs": a["docs"],
                "newest": (datetime.fromtimestamp(a["newest"]).isoformat(timespec="seconds")
                           if a["newest"] else ""),
                "newest_path": a["newest_path"],
                "newest_code": (datetime.fromtimestamp(a["newest_code"]).isoformat(timespec="seconds")
                                if a["newest_code"] else ""),
                "newest_code_path": a["newest_code_path"],
            }
            for name, a in sorted(g.areas.items())
        },
        "doc_lag": [
            {"doc": d, "area": a, "newest_source": s, "days_behind": round(days, 2)}
            for d, a, s, days in g.doc_lag
        ],
        "focus": [n.path for n in g.match(focus)] if focus else [],
    }


def write_json(g: Graph, path: Path, focus=(), extra: dict | None = None) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = to_dict(g, focus=focus)
    if extra:
        payload["extra"] = extra
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def repo_root_from(script_file: str, depth: int = 2) -> Path:
    """Resolve the repository root from a script inside `.subagents/<name>/`."""
    root = Path(script_file).resolve().parents[depth]
    if not (root / "AGENTS.md").is_file():
        raise SystemExit(f"codegraph: {root} does not look like the repository root "
                         f"(no AGENTS.md); refusing to guess")
    return root


if __name__ == "__main__":  # manual smoke use: python3 .subagents/tools/codegraph_core.py
    import argparse

    parser = argparse.ArgumentParser(description="Repository code graph (read-only).")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--json", metavar="PATH")
    parser.add_argument("--top", type=int, default=25)
    parser.add_argument("--md-only", action="store_true")
    args = parser.parse_args()
    graph = build_graph(Path(args.root))
    print(render_text(graph, top=args.top, md_only=args.md_only))
    if args.json:
        print(f"\njson written: {write_json(graph, Path(args.json))}")
