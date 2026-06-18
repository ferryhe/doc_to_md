"""Extract a version section from CHANGELOG.md for GitHub Release notes."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SECTION_HEADING_RE = re.compile(r"^## \[(?P<version>[^\]]+)\].*$", re.MULTILINE)


def extract_changelog_section(changelog_text: str, version: str) -> str:
    headings = list(SECTION_HEADING_RE.finditer(changelog_text))
    for index, heading in enumerate(headings):
        if heading.group("version") != version:
            continue
        start = heading.start()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(changelog_text)
        section = changelog_text[start:end].strip()
        if not section:
            raise ValueError(f"CHANGELOG.md section for [{version}] is empty")
        return section
    raise ValueError(f"CHANGELOG.md does not contain a section for [{version}]")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract release notes for one version from CHANGELOG.md.")
    parser.add_argument("version", help="Version without leading v, for example 0.1.2.")
    parser.add_argument("--changelog", default="CHANGELOG.md", help="Path to CHANGELOG.md.")
    parser.add_argument("--output", help="Optional output file. Defaults to stdout.")
    args = parser.parse_args(argv)

    try:
        text = Path(args.changelog).read_text(encoding="utf-8")
        section = extract_changelog_section(text, args.version)
    except (OSError, ValueError) as exc:
        print(f"changelog extraction error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        Path(args.output).write_text(section + "\n", encoding="utf-8")
    else:
        print(section)
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by CI/CLI
    raise SystemExit(main())
