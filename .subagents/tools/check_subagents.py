#!/usr/bin/env python3
"""Structural gate for the `.subagents` team (the sibling of tools/*_check.sh).

WHAT IT ENFORCES
    1. the seven folders exist and each carries ORIGINAL.md, AGENTS.md,
       SKILL.md, codegraph.py, ERROR.md, REQUESTS.md, PROPOSALS.md and
       reports/latest.json
    2. every SKILL.md is valid under the Agent Skills specification (R35):
       a frontmatter block, pure ASCII, only the documented keys, `name`
       matching `[a-z0-9-]` and the directory name, a quoted `description`
       of at most 1024 characters, a body under 500 lines, and a visible
       trigger ("## When ..." heading or "Use when" in the description)
    3. every codegraph.py declares its own `SUB` (matching the folder) and
       implements its own `extra(` check - a copy-paste stub would fail
    4. ORIGINAL.md records the verbatim owner assignment and a creation date
       (the owner requires it to exist BEFORE the first run)
    5. AGENTS.md states the read-only rule (no sub-agent may edit code)
    6. ERROR.md and REQUESTS.md carry real content - the owner's "every sub
       keeps an error log and can ask questions" directive
    7. no placeholder text in the contract files ("lorem ipsum", "TBD",
       "<placeholder>", "FIXME", "TODO:") - the "no stubs" rule
    8. `--self-test` proves the gate can fail: it copies the tree to a
       temporary directory, breaks one thing per file and requires a red
       result for every defect (R25: a gate that never goes red is decoration)

WHY A GATE
    There is no runtime that loads these folders - they are a contract plus
    tooling. A contract nobody checks decays exactly like prose does, which is
    the finding R33 is built on. The gate is cheap and runs offline.

YAML MODE
    With PyYAML importable the frontmatter is parsed as real YAML (a typo, a
    tab or a duplicated key is a hard error). Without it the gate falls back to
    a top-level `key: value` parser and says so in its first line - the fallback
    is weaker, and pretending otherwise would be the kind of claim this repo
    forbids.

Usage
    python3 .subagents/tools/check_subagents.py
    python3 .subagents/tools/check_subagents.py --self-test
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

try:  # the strict path; CI installs PyYAML, a bare sandbox may not have it
    import yaml  # type: ignore

    HAVE_YAML = True
except ImportError:  # pragma: no cover - environment dependent
    HAVE_YAML = False

TEAM = (
    "web-source-verifier",
    "web-spec-conformance",
    "web-tooling-scout",
    "critic-evidence",
    "critic-architecture",
    "critic-final",
    "ai-threat-scan",
)
REQUIRED = ("ORIGINAL.md", "AGENTS.md", "SKILL.md", "codegraph.py",
            "ERROR.md", "REQUESTS.md", "PROPOSALS.md")
PLACEHOLDERS = ("lorem ipsum", "tbd", "<placeholder>", "fixme", "todo:", "your-name")
READ_ONLY_CLAUSE = "read-only"
MAX_DESCRIPTION_WORDS = 40
MAX_DESCRIPTION_CHARS = 1024
MAX_NAME_CHARS = 64
MAX_BODY_LINES = 500
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata",
                "allowed-tools"}
# Two paths, two jobs (round 15): this is the ONE directory allowed to carry the
# name `sub-agents`. It holds the procedure (SKILL.md). The team - contracts,
# tooling, receipts - lives in `.subagents/`. A second tree with either name is
# the duplicate this check exists to catch.
CANONICAL_SKILL_DIR = ".agents/skills/sub-agents"
WALK_SKIP = {"node_modules", ".git", "vendor", "llama", "__pycache__", "build"}


def _split_frontmatter(text: str):
    if not text.startswith("---\n"):
        return None, "file does not start with a '---' frontmatter block"
    end = text.find("\n---", 4)
    if end < 0:
        return None, "frontmatter block is not terminated by '---'"
    return text[4:end], text[end + 4:].lstrip("\n")


def _fallback_parse(block: str):
    """Top-level `key: value` only; indented block keys are acknowledged, not parsed."""
    data = {}
    for line in block.splitlines():
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            return None, f"frontmatter line is not 'key: value': {line!r}"
        data[match.group(1)] = match.group(2).strip()
    return data, None


def parse_frontmatter(path: Path):
    """Return (dict, error, mode) for one SKILL.md."""
    mode = "yaml" if HAVE_YAML else "fallback"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return None, f"unreadable: {exc}", mode
    block, rest = _split_frontmatter(text)
    if block is None:
        return None, rest, mode
    try:
        block.encode("ascii")
    except UnicodeEncodeError as exc:
        return None, f"frontmatter is not pure ASCII (byte {exc.start}): {exc.object!r}", mode

    # Quoting is a property of the source text, not of the parsed value: PyYAML
    # strips the quotes, so checking the parsed string would reject every legal
    # file. The first version of this function did exactly that and turned all
    # six existing skills red.
    if not re.search(r'(?m)^description:\s*"', block):
        return None, "description must be a quoted scalar (see rules.md R29)", mode

    if HAVE_YAML:
        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError as exc:  # type: ignore[attr-defined]
            first = str(exc).splitlines()[0]
            return None, f"frontmatter is not valid YAML: {first}", mode
        if not isinstance(data, dict):
            return None, "frontmatter is not a mapping", mode
    else:
        data, error = _fallback_parse(block)
        if error:
            return None, error, mode

    unknown = sorted(set(map(str, data)) - ALLOWED_KEYS)
    if unknown:
        return None, (f"unknown frontmatter key(s) {unknown}; the spec allows "
                      f"{sorted(ALLOWED_KEYS)}"), mode
    if "name" not in data:
        return None, "frontmatter has no 'name'", mode
    if "description" not in data:
        return None, "frontmatter has no 'description'", mode

    name = data["name"]
    if not isinstance(name, str):
        return None, "name is not a string", mode
    if len(name) > MAX_NAME_CHARS:
        return None, f"name is {len(name)} chars (limit {MAX_NAME_CHARS})", mode
    if not NAME_RE.match(name):
        return None, f"name {name!r} is not lowercase letters/digits/hyphens", mode

    description = data["description"]
    if not isinstance(description, str):
        return None, "description is not a string", mode
    if not description.strip():
        return None, "description is empty", mode
    if len(description) > MAX_DESCRIPTION_CHARS:
        return None, f"description is {len(description)} chars (limit {MAX_DESCRIPTION_CHARS})", mode
    if "\n" in description.strip():
        return None, "description must be one line", mode
    words = description.strip('"').split()
    if len(words) > MAX_DESCRIPTION_WORDS:
        return None, f"description is {len(words)} words; keep it to one sentence", mode

    tools = data.get("allowed-tools")
    if tools is not None and not isinstance(tools, (str, list)):
        return None, "allowed-tools must be a string or a list", mode

    data["description_text"] = description.strip('"')
    data["body"] = rest
    return data, None, mode


def layout_checks(root: Path, add) -> None:
    """Exactly one `sub-agents` directory, and the two paths point at each other."""
    found = []
    for dirpath, dirnames, _filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root).replace(os.sep, "/")
        rel = "" if rel == "." else rel
        if rel.count("/") >= 3 or rel in WALK_SKIP:
            dirnames[:] = []
            continue
        for name in list(dirnames):
            if name == "sub-agents":
                found.append(f"{rel}/{name}".lstrip("/"))
        dirnames[:] = sorted(d for d in dirnames if d not in WALK_SKIP)

    strays = sorted(p for p in found if p != CANONICAL_SKILL_DIR)
    if strays:
        add("fail", f"duplicate `sub-agents` tree(s) outside {CANONICAL_SKILL_DIR}: {strays}")
    elif not found:
        add("fail", f"{CANONICAL_SKILL_DIR} is missing (the team has no procedure)")
    else:
        add("ok", f"layout: exactly one `sub-agents` directory ({found[0]})")

    skill_dir = root / CANONICAL_SKILL_DIR
    for member_file in ("codegraph.py", "ORIGINAL.md", "PROPOSALS.md", "ERROR.md"):
        if (skill_dir / member_file).is_file():
            add("fail", f"{CANONICAL_SKILL_DIR} contains {member_file}: it is a procedure, "
                        f"not a team member (members live in .subagents/)")

    skill = skill_dir / "SKILL.md"
    if skill.is_file() and ".subagents/" not in skill.read_text(encoding="utf-8", errors="replace"):
        add("fail", f"{CANONICAL_SKILL_DIR}/SKILL.md does not point at .subagents/ "
                    f"(a stale copy would be a second, contradictory procedure)")

    readme = root / ".subagents" / "README.md"
    if readme.is_file() and CANONICAL_SKILL_DIR not in readme.read_text(encoding="utf-8", errors="replace"):
        add("fail", ".subagents/README.md does not name its parent procedure "
                    f"({CANONICAL_SKILL_DIR})")


def has_visible_trigger(front: dict) -> bool:
    body = front.get("body") or ""
    if re.search(r"(?m)^##\s+When\b", body):
        return True
    return "use when" in front["description_text"].lower()


def check(root: Path, verbose: bool = True):
    """Return a list of (level, message); level is 'ok', 'fail' or 'warn'."""
    results = []

    def add(level, message):
        results.append((level, message))
        if verbose:
            print(f"{level.upper():<5} {message}")

    subs_dir = root / ".subagents"
    if not subs_dir.is_dir():
        add("fail", ".subagents/ does not exist")
        return results
    add("ok", "frontmatter parser: " + ("PyYAML (strict, full YAML)" if HAVE_YAML
                                        else "structural fallback (PyYAML not installed)"))

    for name in TEAM:
        folder = subs_dir / name
        if not folder.is_dir():
            add("fail", f"{name}: folder missing")
            continue
        for required in REQUIRED:
            path = folder / required
            if not path.is_file():
                add("fail", f"{name}: {required} missing")
            elif path.stat().st_size == 0:
                add("fail", f"{name}: {required} is empty")

        skill = folder / "SKILL.md"
        if skill.is_file():
            front, error, _mode = parse_frontmatter(skill)
            if error:
                add("fail", f"{name}: SKILL.md frontmatter - {error}")
            else:
                if front["name"] != name:
                    add("fail", f"{name}: SKILL.md name '{front['name']}' != folder name")
                body_lines = len(front["body"].splitlines())
                if body_lines > MAX_BODY_LINES:
                    add("fail", f"{name}: SKILL.md body is {body_lines} lines "
                                f"(limit {MAX_BODY_LINES}; progressive disclosure)")
                if not has_visible_trigger(front):
                    add("fail", f"{name}: SKILL.md has no visible trigger "
                                f"(a '## When' heading or 'Use when' in the description)")
                if not error and front["name"] == name and body_lines <= MAX_BODY_LINES \
                        and has_visible_trigger(front):
                    add("ok", f"{name}: SKILL.md valid ({body_lines} body lines, "
                              f"{len(front['description_text'])} char description)")

        script = folder / "codegraph.py"
        if script.is_file():
            text = script.read_text(encoding="utf-8", errors="replace")
            if f'SUB = "{name}"' not in text:
                add("fail", f"{name}: codegraph.py does not declare SUB = \"{name}\"")
            if "def extra(" not in text:
                add("fail", f"{name}: codegraph.py has no own extra() check")
            if "codegraph_core" not in text:
                add("fail", f"{name}: codegraph.py does not use the shared engine")

        original = folder / "ORIGINAL.md"
        if original.is_file():
            text = original.read_text(encoding="utf-8", errors="replace")
            if "Original owner assignment" not in text:
                add("fail", f"{name}: ORIGINAL.md has no verbatim owner-assignment section")
            if not re.search(r"Created \| 20\d\d-\d\d-\d\d", text):
                add("fail", f"{name}: ORIGINAL.md has no creation date")
            if "Created **before this sub-agent's first run**" not in text:
                add("fail", f"{name}: ORIGINAL.md does not record that it predates the run")

        agents = folder / "AGENTS.md"
        if agents.is_file():
            text = agents.read_text(encoding="utf-8", errors="replace")
            if READ_ONLY_CLAUSE not in text.lower():
                add("fail", f"{name}: AGENTS.md does not state the read-only rule")
            else:
                add("ok", f"{name}: AGENTS.md states the read-only rule")

        # The owner's directive: every sub keeps an error log and may ask
        # questions. Content, not just existence - an empty log is a stub.
        for bookkeeping, minimum in (("ERROR.md", 400), ("REQUESTS.md", 300)):
            path = folder / bookkeeping
            if path.is_file() and path.stat().st_size < minimum:
                add("fail", f"{name}: {bookkeeping} is {path.stat().st_size} B "
                            f"(under {minimum} B - looks like a placeholder)")

        for contract in ("ORIGINAL.md", "AGENTS.md", "SKILL.md", "ERROR.md", "REQUESTS.md"):
            path = folder / contract
            if not path.is_file():
                continue
            lowered = path.read_text(encoding="utf-8", errors="replace").lower()
            for token in PLACEHOLDERS:
                if token in lowered:
                    add("fail", f"{name}: {contract} contains placeholder text {token!r}")

        report = folder / "reports" / "latest.json"
        if report.is_file():
            try:
                payload = json.loads(report.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                add("fail", f"{name}: reports/latest.json is not valid JSON ({exc})")
            else:
                stats = payload.get("stats") or {}
                if not stats.get("files"):
                    add("fail", f"{name}: reports/latest.json has no file inventory")
                else:
                    add("ok", f"{name}: report describes {stats['files']} files")

    team_skill = find_parent_skill(root)
    if team_skill is None:
        add("fail", ".agents/skills/sub-agents/SKILL.md (the parent skill) is missing")
    else:
        front, error, _mode = parse_frontmatter(team_skill)
        if error:
            add("fail", f"sub-agents skill frontmatter - {error}")
        elif front["name"] != "sub-agents":
            add("fail", f"sub-agents skill name '{front['name']}' != 'sub-agents'")
        else:
            add("ok", "sub-agents parent skill: frontmatter valid")

    layout_checks(root, add)

    failures = [m for level, m in results if level == "fail"]
    add("ok" if not failures else "fail",
        f"summary: {len(TEAM)} folders checked, {len(failures)} failure(s)")
    return results


def find_parent_skill(root: Path):
    for candidate in (".agents/skills/sub-agents/SKILL.md",
                      ".claude/skills/sub-agents/SKILL.md"):
        path = root / candidate
        if path.is_file():
            return path
    return None


def self_test(root: Path) -> int:
    """R25 negative control: the gate must reject a broken copy of the tree.

    One defect per FILE. The first version of this control put a bad name and an
    unquoted description in the same file; the parser stopped at the first error,
    so it proved one detector and claimed three.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp) / "repo"
        shutil.copytree(root / ".subagents", tmp_root / ".subagents",
                        ignore=shutil.ignore_patterns("__pycache__", "reports"))
        parent = find_parent_skill(root)
        if parent is None:
            print("SELF-TEST FAIL - the parent skill is missing, cannot copy it")
            return 1
        shutil.copytree(parent.parent, tmp_root / ".agents" / "skills" / "sub-agents")
        for name in TEAM:  # the gate requires a report per folder
            reports = tmp_root / ".subagents" / name / "reports"
            reports.mkdir(parents=True, exist_ok=True)
            (reports / "latest.json").write_text('{"stats": {"files": 1}}\n', encoding="utf-8")

        before = [level for level, _ in check(tmp_root, verbose=False)]
        if "fail" in before:
            print("SELF-TEST FAIL - the copied tree is already red; fix the tree "
                  "before trusting the control")
            return 1

        subs = tmp_root / ".subagents"
        # 1. unquoted description
        (subs / "critic-evidence" / "SKILL.md").write_text(
            "---\nname: critic-evidence\ndescription: unquoted description\n---\n\n# broken\n",
            encoding="utf-8")
        # 2. name that does not match the folder
        (subs / "critic-architecture" / "SKILL.md").write_text(
            '---\nname: wrong-name\ndescription: "A quoted sentence that is otherwise fine."\n'
            "---\n\n# broken\n## When to use\n", encoding="utf-8")
        # 3. empty proposals file
        (subs / "web-tooling-scout" / "PROPOSALS.md").write_text("", encoding="utf-8")
        # 4. unknown frontmatter key (a typo a loader would ignore silently)
        (subs / "web-spec-conformance" / "SKILL.md").write_text(
            '---\nname: web-spec-conformance\nnmae: typo\n'
            'description: "Use when testing an unknown key."\n---\n\n# broken\n',
            encoding="utf-8")
        # 5. no visible trigger: no "## When" heading and no "Use when"
        (subs / "web-source-verifier" / "SKILL.md").write_text(
            '---\nname: web-source-verifier\ndescription: "Verifies external claims."\n'
            "---\n\n# broken\n## Procedure\n", encoding="utf-8")
        # 6. missing error log + 7. an oversized body (different files in one folder)
        (subs / "critic-final" / "ERROR.md").unlink()
        # 8. a second, non-canonical `sub-agents` tree at the repository root
        stray = tmp_root / "sub-agents"
        stray.mkdir()
        (stray / "SKILL.md").write_text(
            '---\nname: sub-agents\ndescription: "A second copy that must be rejected."\n'
            "---\n\n# copy\n", encoding="utf-8")
        (subs / "critic-final" / "SKILL.md").write_text(
            '---\nname: critic-final\ndescription: "Use when grading a round."\n---\n\n'
            "# broken\n## When to use\n" + "\nfiller\n" * (MAX_BODY_LINES + 10),
            encoding="utf-8")

        after = check(tmp_root, verbose=False)
        failures = [message for level, message in after if level == "fail"]
        expectations = (
            ("quoted scalar", "unquoted description"),
            ("name 'wrong-name'", "name != folder"),
            ("PROPOSALS.md is empty", "empty proposals"),
            ("unknown frontmatter key", "unknown frontmatter key"),
            ("no visible trigger", "missing trigger"),
            ("ERROR.md missing", "missing ERROR.md"),
            (f"limit {MAX_BODY_LINES}", "oversized body"),
            ("duplicate `sub-agents` tree", "duplicate sub-agents tree"),
        )
        missed = 0
        for fragment, label in expectations:
            if any(fragment in message for message in failures):
                continue
            missed += 1
            print(f"SELF-TEST FAIL - the broken copy was accepted for: {label} ({fragment!r})")
        if missed:
            return 1
        if "fail" not in [level for level, _ in after]:
            print("SELF-TEST FAIL - the gate stayed green on the broken copy")
            return 1
        print(f"SELF-TEST ok - the broken copy was rejected on all {len(expectations)} "
              f"deliberate defects (7 member-file defects from rounds 12-14 + the "
              f"duplicate-tree control added in round 15)")
        return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Structural gate for .subagents/.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--self-test", action="store_true",
                        help="prove the gate can fail (R25 negative control)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    results = check(root, verbose=not args.quiet)
    failures = [message for level, message in results if level == "fail"]
    if args.self_test:
        return self_test(root)
    print(f"\nCHECK-SUBAGENTS: {'ok' if not failures else 'FAIL'} "
          f"({len(results)} checks, {len(failures)} failure(s))")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
