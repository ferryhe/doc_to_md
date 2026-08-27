import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

from packaging.requirements import Requirement
from packaging.version import Version


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WATCH_FILE = PROJECT_ROOT / "requirements-upstream-watch.txt"


def _watched_versions() -> dict[str, Version]:
    versions: dict[str, Version] = {}
    for raw_line in WATCH_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"(?P<name>[A-Za-z0-9_.-]+)==(?P<version>[^\s]+)", line)
        assert match is not None, f"watch entries must use exact pins: {line}"
        versions[match.group("name").lower()] = Version(match.group("version"))
    return versions


def _project_requirements() -> dict[str, Requirement]:
    project = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    raw_requirements = list(project["dependencies"])
    for requirements in project["optional-dependencies"].values():
        raw_requirements.extend(requirements)
    return {Requirement(raw).name.lower(): Requirement(raw) for raw in raw_requirements}


def test_watched_converter_versions_stay_inside_project_ranges() -> None:
    watched = _watched_versions()
    project = _project_requirements()

    for name in (
        "mistralai",
        "openai",
        "markitdown",
        "paddleocr",
        "mineru",
        "docling",
        "opendataloader-pdf",
    ):
        assert watched[name] in project[name].specifier


def test_marker_is_monitored_but_not_offered_as_a_broken_extra() -> None:
    watched = _watched_versions()
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert watched["marker-pdf"] == Version("2.0.0")
    assert "marker" not in pyproject["project"]["optional-dependencies"]
    assert "Marker is watch-only" in WATCH_FILE.read_text(encoding="utf-8")
