#!/usr/bin/env python3
"""Block delivery when a Markdown draft drifts from its refined outline."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
ALLOWED_EXTRA_HEADINGS = {
    "summary",
    "摘要",
    "概要",
    "references",
    "参考资料",
    "参考文献",
    "evidence notes",
    "证据说明",
    "limitations",
    "局限",
    "局限性",
    "further research",
    "后续研究",
    "verification notes",
    "验证说明",
}


@dataclass(frozen=True)
class Heading:
    level: int
    title: str
    normalized: str
    line_no: int
    body: str


def normalize_title(title: str) -> str:
    normalized = unicodedata.normalize("NFKC", title).strip()
    normalized = normalized.replace("`", "").replace("**", "")
    return " ".join(normalized.casefold().split())


def parse_headings(text: str) -> list[Heading]:
    lines = text.splitlines()
    raw: list[tuple[int, str, int]] = []
    in_fence = False

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if match:
            raw.append((len(match.group(1)), match.group(2).strip(), index))

    headings: list[Heading] = []
    for position, (level, title, index) in enumerate(raw):
        next_index = raw[position + 1][2] if position + 1 < len(raw) else len(lines)
        body = "\n".join(lines[index + 1 : next_index]).strip()
        headings.append(
            Heading(level, title, normalize_title(title), index + 1, body)
        )
    return headings


def without_document_title(headings: list[Heading]) -> list[Heading]:
    if headings and headings[0].level == 1:
        return headings[1:]
    return headings


def is_leaf(headings: list[Heading], index: int) -> bool:
    current_level = headings[index].level
    if index + 1 >= len(headings):
        return True
    return headings[index + 1].level <= current_level


def meaningful_body(body: str) -> bool:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("<!--"):
            return True
    return False


def lint_structure(outline_path: Path, report_path: Path) -> int:
    outline = without_document_title(
        parse_headings(outline_path.read_text(encoding="utf-8"))
    )
    report = without_document_title(
        parse_headings(report_path.read_text(encoding="utf-8"))
    )
    issues: list[str] = []

    if not outline:
        issues.append("Refined outline has no substantive headings.")
    if not report:
        issues.append("Final report has no substantive headings.")
    if issues:
        return print_issues(issues)

    matched_report_indexes: set[int] = set()
    cursor = 0
    matches: list[tuple[int, int]] = []

    for outline_index, expected in enumerate(outline):
        match_index = next(
            (
                index
                for index in range(cursor, len(report))
                if report[index].normalized == expected.normalized
                and report[index].level == expected.level
            ),
            None,
        )
        if match_index is None:
            same_title = [item for item in report if item.normalized == expected.normalized]
            if same_title:
                levels = ", ".join(f"H{item.level} line {item.line_no}" for item in same_title)
                issues.append(
                    f"Level or order mismatch for outline H{expected.level} '{expected.title}' "
                    f"(line {expected.line_no}); report occurrences: {levels}."
                )
            else:
                issues.append(
                    f"Missing outline H{expected.level} '{expected.title}' "
                    f"from report (outline line {expected.line_no})."
                )
            continue
        matched_report_indexes.add(match_index)
        matches.append((outline_index, match_index))
        cursor = match_index + 1

    for report_index, actual in enumerate(report):
        if report_index in matched_report_indexes:
            continue
        if actual.normalized not in ALLOWED_EXTRA_HEADINGS:
            issues.append(
                f"Unapproved extra H{actual.level} '{actual.title}' on report line "
                f"{actual.line_no}; add it to the refined outline or remove it."
            )

    for outline_index, report_index in matches:
        if is_leaf(outline, outline_index) and not meaningful_body(report[report_index].body):
            actual = report[report_index]
            issues.append(
                f"Empty leaf section H{actual.level} '{actual.title}' on report line "
                f"{actual.line_no}."
            )

    if issues:
        return print_issues(issues)

    print(
        "Report structure lint passed: "
        f"{len(outline)} outline headings matched in order; all leaf sections contain content."
    )
    return 0


def print_issues(issues: list[str]) -> int:
    print("Report structure lint blocked delivery:")
    for issue in issues:
        print(f"- {issue}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare a final Markdown report against its locked refined outline."
    )
    parser.add_argument("outline", type=Path, help="Path to refined-outline.md")
    parser.add_argument("report", type=Path, help="Path to the final Markdown draft")
    args = parser.parse_args()

    for label, path in (("Outline", args.outline), ("Report", args.report)):
        if not path.exists():
            print(f"{label} file not found: {path}", file=sys.stderr)
            return 2
        if not path.is_file():
            print(f"{label} path is not a file: {path}", file=sys.stderr)
            return 2

    return lint_structure(args.outline, args.report)


if __name__ == "__main__":
    raise SystemExit(main())
