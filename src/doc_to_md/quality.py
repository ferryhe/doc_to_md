"""Heuristic quality checks for converted Markdown."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import re

IMAGE_RE = re.compile(r"!\[[^\]]*]\(([^)]+)\)")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+\S")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+\S")
TABLE_RE = re.compile(r"^\s*\|.*\|\s*$")
FORMULA_KEYWORDS = ("公式", "计算公式", "如下", "其中", "矩阵", "相关系数", "min", "max")
MATH_SEGMENT_PATTERN = re.compile(
    r"(?P<fenced_math>```(?:math|latex)\s*[\r\n]+.*?[\r\n]*```)"
    r"|(?P<display_dollar>\$\$.*?\$\$)"
    r"|(?P<display_bracket>\\\[.*?\\\])"
    r"|(?P<inline_paren>\\\(.*?\\\))"
    r"|(?P<inline_dollar>(?<!\$)\$(?!\$).*?(?<!\\)\$)",
    re.DOTALL | re.IGNORECASE,
)
HTML_ENTITY_RE = re.compile(r"&(?:lt|gt|amp|nbsp|#\d+|#x[0-9a-fA-F]+);", re.IGNORECASE)
PLACEHOLDER_PATTERNS = (
    re.compile(r"_No text detected\._"),
    re.compile(r"_No content returned by [^_]+?_\."),
    re.compile(r"\[Image OCR failed: [^\]]+\]"),
)
FRAGMENTED_NUMBER_RE = re.compile(r"\b\d\s+\.\s+\d\b|\b\d(?:\s+\d){2,}\b")
FRAGMENTED_SYMBOL_RE = re.compile(r"\b(?:[A-Za-z]\s+){2,}[A-Za-z]\b")


@dataclass(slots=True)
class MarkdownDiagnostic:
    code: str
    severity: str
    message: str
    count: int = 1


@dataclass(slots=True)
class MarkdownQualityReport:
    status: str
    formula_status: str
    headings: int
    bullet_lines: int
    table_lines: int
    image_references: int
    formula_image_references: int
    inline_math_segments: int
    block_math_segments: int
    diagnostics: list[MarkdownDiagnostic] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def evaluate_markdown_quality(markdown: str) -> MarkdownQualityReport:
    lines = markdown.splitlines()
    matches = list(MATH_SEGMENT_PATTERN.finditer(markdown))
    math_segments = [match.group(0) for match in matches]
    inline_math_segments = sum(
        1 for match in matches if match.group("inline_paren") or match.group("inline_dollar")
    )
    block_math_segments = sum(
        1
        for match in matches
        if match.group("fenced_math") or match.group("display_dollar") or match.group("display_bracket")
    )
    image_references = sum(len(list(IMAGE_RE.finditer(line))) for line in lines)
    formula_image_references = _count_formula_image_references(lines)

    diagnostics: list[MarkdownDiagnostic] = []

    if formula_image_references:
        diagnostics.append(
            MarkdownDiagnostic(
                code="formula_image_reference",
                severity="error",
                message="Potential formula images remain in the Markdown output.",
                count=formula_image_references,
            )
        )

    entity_hits = sum(len(HTML_ENTITY_RE.findall(segment)) for segment in math_segments)
    if entity_hits:
        diagnostics.append(
            MarkdownDiagnostic(
                code="math_html_entity",
                severity="warning",
                message="HTML entities are still present inside math segments.",
                count=entity_hits,
            )
        )

    placeholder_hits = sum(len(pattern.findall(markdown)) for pattern in PLACEHOLDER_PATTERNS)
    if placeholder_hits:
        diagnostics.append(
            MarkdownDiagnostic(
                code="ocr_placeholder",
                severity="warning",
                message="OCR placeholder text is present in the Markdown output.",
                count=placeholder_hits,
            )
        )

    fragmented_hits = count_fragmented_math_segments(math_segments)
    if fragmented_hits:
        diagnostics.append(
            MarkdownDiagnostic(
                code="fragmented_math_tokens",
                severity="warning",
                message="Some math segments still look fragmented by OCR spacing.",
                count=fragmented_hits,
            )
        )

    if _has_unbalanced_display_math(markdown):
        diagnostics.append(
            MarkdownDiagnostic(
                code="unbalanced_display_math",
                severity="error",
                message="Display math delimiters look unbalanced.",
            )
        )

    formula_related = bool(
        formula_image_references
        or inline_math_segments
        or block_math_segments
        or _contains_formula_keywords(markdown)
    )
    if formula_related and not (formula_image_references or inline_math_segments or block_math_segments):
        diagnostics.append(
            MarkdownDiagnostic(
                code="formula_context_without_math",
                severity="warning",
                message="Formula-like context was detected, but no math segments were recovered.",
            )
        )

    status = _derive_status(diagnostics)
    formula_status = _derive_formula_status(diagnostics, formula_related)
    return MarkdownQualityReport(
        status=status,
        formula_status=formula_status,
        headings=sum(1 for line in lines if HEADING_RE.match(line)),
        bullet_lines=sum(1 for line in lines if BULLET_RE.match(line)),
        table_lines=sum(1 for line in lines if TABLE_RE.match(line)),
        image_references=image_references,
        formula_image_references=formula_image_references,
        inline_math_segments=inline_math_segments,
        block_math_segments=block_math_segments,
        diagnostics=diagnostics,
    )


def _count_formula_image_references(lines: list[str]) -> int:
    formula_images = 0
    for index, line in enumerate(lines):
        matches = list(IMAGE_RE.finditer(line))
        if not matches:
            continue
        if _looks_formula_like_context(lines, index):
            formula_images += len(matches)
    return formula_images


def _looks_formula_like_context(lines: list[str], index: int) -> bool:
    line = lines[index]
    if "|" in line and "---" not in line:
        return True
    tokens = list(IMAGE_RE.finditer(line))
    if len(tokens) == 1 and line.strip() == tokens[0].group(0):
        return True
    return _contains_formula_keywords(_context_window(lines, index))


def _context_window(lines: list[str], index: int, radius: int = 1) -> str:
    start = max(0, index - radius)
    end = min(len(lines), index + radius + 1)
    return "\n".join(lines[start:end])


def _contains_formula_keywords(text: str) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in FORMULA_KEYWORDS)


def extract_math_segments(markdown: str) -> list[str]:
    return [match.group(0) for match in MATH_SEGMENT_PATTERN.finditer(markdown)]


def count_fragmented_math_segments(segments: list[str]) -> int:
    fragmented = 0
    for segment in segments:
        if FRAGMENTED_NUMBER_RE.search(segment) or FRAGMENTED_SYMBOL_RE.search(segment):
            fragmented += 1
    return fragmented


def _has_unbalanced_display_math(markdown: str) -> bool:
    if len(re.findall(r"(?<!\\)\$\$", markdown)) % 2 != 0:
        return True
    if len(re.findall(r"\\\[", markdown)) != len(re.findall(r"\\\]", markdown)):
        return True
    return False


def _derive_status(diagnostics: list[MarkdownDiagnostic]) -> str:
    severities = {item.severity for item in diagnostics}
    if "error" in severities:
        return "poor"
    if "warning" in severities:
        return "review"
    return "good"


def _derive_formula_status(diagnostics: list[MarkdownDiagnostic], formula_related: bool) -> str:
    if not formula_related:
        return "not_applicable"
    formula_diagnostics = [item for item in diagnostics if item.code.startswith("formula_") or "math" in item.code]
    if any(item.severity == "error" for item in formula_diagnostics):
        return "poor"
    if any(item.severity == "warning" for item in formula_diagnostics):
        return "review"
    return "good"
