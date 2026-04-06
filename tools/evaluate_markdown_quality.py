"""Evaluate converted Markdown quality from the repository root."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> int:
    from doc_to_md.quality import evaluate_markdown_quality

    parser = argparse.ArgumentParser(description="Inspect Markdown quality for agent workflows.")
    parser.add_argument("markdown_path", type=Path, help="Path to a Markdown file")
    parser.add_argument("--json", action="store_true", help="Emit a JSON report")
    args = parser.parse_args()

    report = evaluate_markdown_quality(args.markdown_path.read_text(encoding="utf-8"))
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 0

    print(f"status={report.status}")
    print(f"formula_status={report.formula_status}")
    print(f"headings={report.headings}")
    print(f"bullet_lines={report.bullet_lines}")
    print(f"table_lines={report.table_lines}")
    print(f"image_references={report.image_references}")
    print(f"formula_image_references={report.formula_image_references}")
    print(f"inline_math_segments={report.inline_math_segments}")
    print(f"block_math_segments={report.block_math_segments}")
    if report.diagnostics:
        print("diagnostics:")
        for item in report.diagnostics:
            print(f"- {item.severity}:{item.code}:{item.count}:{item.message}")
    else:
        print("diagnostics: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
