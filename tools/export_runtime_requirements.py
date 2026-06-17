"""Export the package's direct runtime dependencies for security audit jobs."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


DEPENDENCIES_RE = re.compile(r"^dependencies\s*=\s*\[(?P<body>.*?)^\]", re.MULTILINE | re.DOTALL)
REQUIREMENT_RE = re.compile(r'"([^"]+)"')


def project_dependencies(pyproject_text: str) -> list[str]:
    match = DEPENDENCIES_RE.search(pyproject_text)
    if match is None:
        raise ValueError("pyproject.toml does not contain a [project] dependencies array")
    return REQUIREMENT_RE.findall(match.group("body"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write direct runtime dependencies from pyproject.toml.")
    parser.add_argument("--pyproject", default="pyproject.toml")
    parser.add_argument("--output", help="Optional output path. Defaults to stdout.")
    args = parser.parse_args(argv)

    dependencies = project_dependencies(Path(args.pyproject).read_text(encoding="utf-8"))
    payload = "\n".join(dependencies) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by CI/CLI
    raise SystemExit(main())
