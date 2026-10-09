#!/usr/bin/env python3
"""Validate local Markdown links (Python standard library only).

Usage: python3 scripts/check_docs.py [--strict-anchors]
Default checks paths; strict mode also checks fragment IDs. External URLs are not fetched.
"""
from __future__ import annotations
import argparse
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]\n]*\]\((<[^>\n]+>|[^\s)\n]+)(?:\s+['\"][^)\n]*['\"])?\)")
REFERENCE = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*<?([^\s>]+)>?(?:\s+.*)?$")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s{0,3}(\x60{3,}|~{3,})")


def slug(title: str) -> str:
    """Approximate GitHub heading IDs for optional strict checks."""
    title = re.sub(r"<[^>]+>", "", title).replace(chr(96), "").replace("*", "")
    title = title.lower()
    return "".join(
        c if c in " -_" or unicodedata.category(c)[0] in ("L", "N") else ""
        for c in title
    ).replace(" ", "-")


def ids(file: Path) -> set[str]:
    headings: dict[str, int] = {}
    anchors: set[str] = set()
    in_fence = False
    for line in file.read_text(encoding="utf-8").splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING.match(line)
        if match:
            name = slug(match.group(1))
            count = headings.get(name, 0)
            headings[name] = count + 1
            anchors.add(name if count == 0 else f"{name}-{count}")
        for a in re.finditer(r'<a\s+(?:name|id)=["\']([^"\']+)["\']', line, re.I):
            anchors.add(a.group(1))
    return anchors


def resolve_link(file: Path, destination: str, strict: bool) -> str | None:
    dest = destination.strip("<>")
    uri = urlsplit(dest)
    if uri.scheme or uri.netloc or dest.startswith("//"):
        return None
    if uri.path.startswith("/"):
        return None  # URL or absolute application route outside local file links.
    target = (file.parent / unquote(uri.path)).resolve() if uri.path else file
    try:
        target.relative_to(REPO)
    except ValueError:
        return "escapes repository"
    if target.is_dir():
        if not (target / "README.md").is_file():
            return "directory has no README.md"
        target = target / "README.md"
    if not target.is_file():
        return "file does not exist"
    if strict and uri.fragment and target.suffix.lower() == ".md":
        if unquote(uri.fragment) not in ids(target):
            return f"heading anchor #{uri.fragment} not found"
    return None


def scan(file: Path, strict: bool) -> tuple[int, list[str]]:
    lines = file.read_text(encoding="utf-8").splitlines()
    refs = {}
    for line in lines:
        match = REFERENCE.match(line)
        if match:
            refs[match.group(1).lower()] = match.group(2)
    issues: list[str] = []
    count = 0
    in_fence = False
    for number, line in enumerate(lines, start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        targets = [m.group(1) for m in LINK.finditer(line)]
        for m in re.finditer(r"(?<!!)\[[^\]\n]+\]\[([^\]\n]+)\]", line):
            ref = refs.get(m.group(1).lower())
            if ref:
                targets.append(ref)
        for dest in targets:
            count += 1
            result = resolve_link(file, dest, strict)
            if result:
                issues.append(f"{file.relative_to(REPO)}:{number}: {dest}: {result}")
    return count, issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict-anchors", action="store_true")
    args = parser.parse_args()
    files = sorted(REPO.rglob("*.md"))
    excluded = {".git", "node_modules", ".dart_tool", "target", "build", ".venv"}
    files = [f for f in files if not excluded.intersection(f.relative_to(REPO).parts)]
    failures: list[str] = []
    links = 0
    for file in files:
        count, errors = scan(file, args.strict_anchors)
        links += count
        failures += errors
    for failure in failures:
        print("ERROR:", failure)
    print(f"Checked {len(files)} Markdown files, {links} links; {len(failures)} errors")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
