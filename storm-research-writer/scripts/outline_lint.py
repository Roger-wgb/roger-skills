#!/usr/bin/env python3
"""Lightweight Markdown outline checks for STORM-style research drafts."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def parse_headings(text: str) -> list[tuple[int, str, int]]:
    headings: list[tuple[int, str, int]] = []
    in_fence = False

    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        match = HEADING_RE.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            headings.append((level, title, line_no))

    return headings


def lint_outline(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    headings = parse_headings(text)
    issues: list[str] = []

    if not headings:
        issues.append("No Markdown headings found.")
    else:
        min_level = min(level for level, _, _ in headings)
        if min_level > 2:
            issues.append("Outline starts too deep; add a top-level or second-level heading.")

    normalized_titles = [title.lower() for _, title, _ in headings]
    duplicates = [title for title, count in Counter(normalized_titles).items() if count > 1]
    for duplicate in duplicates:
        lines = [str(line_no) for _, title, line_no in headings if title.lower() == duplicate]
        issues.append(f"Duplicate heading '{duplicate}' on lines {', '.join(lines)}.")

    previous_level = None
    for level, title, line_no in headings:
        if previous_level is not None and level > previous_level + 1:
            issues.append(
                f"Heading level jumps on line {line_no}: '{title}' goes from H{previous_level} to H{level}."
            )
        previous_level = level

    # Real placeholders that signal an unfinished outline — treated as issues.
    placeholder_markers = (
        "todo",
        "tbd",
        "misc",
        "stuff",
        "杂项",
        "待补充",
    )
    # Generic-but-legitimate section names (an Overview or Background section is
    # normal, and the skill's own output templates use them). These are advisory
    # only: flag them as notes, not failures.
    generic_markers = (
        "other",
        "various",
        "其他",
        "概述",
        "背景介绍",
    )
    notes: list[str] = []
    for _, title, line_no in headings:
        normalized = title.strip().lower()
        if normalized in placeholder_markers:
            issues.append(f"Placeholder heading on line {line_no}: '{title}'.")
        elif normalized in generic_markers:
            notes.append(
                f"Generic heading on line {line_no}: '{title}' — acceptable if "
                "intentional, but a topic-specific title is usually stronger."
            )

    if issues:
        print("Outline lint found issues:")
        for issue in issues:
            print(f"- {issue}")
        for note in notes:
            print(f"- (note) {note}")
        return 1

    if notes:
        print("Outline lint passed with notes:")
        for note in notes:
            print(f"- {note}")
        return 0

    print("Outline lint passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a Markdown outline for basic structural issues.")
    parser.add_argument("outline", type=Path, help="Path to a Markdown outline file")
    args = parser.parse_args()

    if not args.outline.exists():
        print(f"File not found: {args.outline}", file=sys.stderr)
        return 2
    if not args.outline.is_file():
        print(f"Not a file: {args.outline}", file=sys.stderr)
        return 2

    return lint_outline(args.outline)


if __name__ == "__main__":
    raise SystemExit(main())
