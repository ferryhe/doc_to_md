"""Export the package's direct runtime dependencies for security audit jobs."""
from __future__ import annotations

import argparse
from pathlib import Path

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib  # type: ignore[no-redef]


def project_dependencies(pyproject_text: str) -> list[str]:
    data = tomllib.loads(pyproject_text)
    project = data.get("project")
    if not isinstance(project, dict):
        raise ValueError("pyproject.toml does not contain a [project] table")
    dependencies = project.get("dependencies")
    if not isinstance(dependencies, list):
        raise ValueError("pyproject.toml does not contain [project].dependencies")
    if not all(isinstance(requirement, str) for requirement in dependencies):
        raise ValueError("[project].dependencies must contain only strings")
    return dependencies


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
