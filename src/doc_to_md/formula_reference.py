"""Reference-aware math readability checks for converted Markdown."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from difflib import SequenceMatcher
import re

from doc_to_md.quality import count_fragmented_math_segments, extract_math_segments

FENCE_WRAPPER_RE = re.compile(
    r"^```(?:math|latex)\s*[\r\n]+(?P<body>.*?)[\r\n]*```$",
    re.DOTALL | re.IGNORECASE,
)
WRAPPER_COMMAND_RE = re.compile(
    r"\\(?:mathrm|mathbf|mathit|text|operatorname|boldsymbol)\s*\{([^{}]*)\}"
)
ENVIRONMENT_RE = re.compile(r"\\(?:begin|end)\{[^{}]+\}")
SPACING_COMMAND_RE = re.compile(r"\\(?:left|right|quad|qquad|,|;|:|!|enspace|thinspace)(?![A-Za-z])")


@dataclass(slots=True)
class FormulaReferenceDiagnostic:
    code: str
    severity: str
    message: str
    count: int = 1


@dataclass(slots=True)
class FormulaReferenceReport:
    status: str
    reference_formula_count: int
    candidate_formula_count: int
    matched_formula_count: int
    missing_formula_count: int
    extra_formula_count: int
    fragmented_candidate_formula_count: int
    formula_recall: float
    average_similarity: float
    diagnostics: list[FormulaReferenceDiagnostic] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def evaluate_formula_reference(
    candidate_markdown: str,
    reference_markdown: str,
    *,
    match_threshold: float = 0.65,
) -> FormulaReferenceReport:
    candidate_segments = extract_math_segments(candidate_markdown)
    reference_segments = extract_math_segments(reference_markdown)

    if not reference_segments:
        return FormulaReferenceReport(
            status="not_applicable",
            reference_formula_count=0,
            candidate_formula_count=len(candidate_segments),
            matched_formula_count=0,
            missing_formula_count=0,
            extra_formula_count=len(candidate_segments),
            fragmented_candidate_formula_count=count_fragmented_math_segments(candidate_segments),
            formula_recall=1.0,
            average_similarity=1.0,
            diagnostics=[],
        )

    candidate_normalized = [_normalize_math_segment(segment) for segment in candidate_segments]
    reference_normalized = [_normalize_math_segment(segment) for segment in reference_segments]
    fragmented_count = count_fragmented_math_segments(candidate_segments)

    unmatched_candidate_indices = set(range(len(candidate_normalized)))
    matched_formula_count = 0
    best_scores: list[float] = []
    for reference_unit in reference_normalized:
        best_index = None
        best_score = 0.0
        for candidate_index in unmatched_candidate_indices:
            score = SequenceMatcher(None, reference_unit, candidate_normalized[candidate_index]).ratio()
            if score > best_score:
                best_score = score
                best_index = candidate_index
        best_scores.append(best_score)
        if best_index is not None and best_score >= match_threshold:
            unmatched_candidate_indices.remove(best_index)
            matched_formula_count += 1

    reference_formula_count = len(reference_segments)
    candidate_formula_count = len(candidate_segments)
    missing_formula_count = reference_formula_count - matched_formula_count
    extra_formula_count = max(0, candidate_formula_count - matched_formula_count)
    formula_recall = matched_formula_count / reference_formula_count
    average_similarity = sum(best_scores) / reference_formula_count

    diagnostics: list[FormulaReferenceDiagnostic] = []
    if candidate_formula_count == 0:
        diagnostics.append(
            FormulaReferenceDiagnostic(
                code="reference_formula_missing_all",
                severity="error",
                message="No explicit math segments were recovered compared with the reviewed reference Markdown.",
            )
        )
    elif missing_formula_count:
        severity = "error" if formula_recall < 0.5 else "warning"
        diagnostics.append(
            FormulaReferenceDiagnostic(
                code="reference_formula_missing",
                severity=severity,
                message="Some reviewed reference formulas were not recovered as explicit math segments.",
                count=missing_formula_count,
            )
        )

    if average_similarity < 0.85:
        diagnostics.append(
            FormulaReferenceDiagnostic(
                code="reference_formula_low_similarity",
                severity="warning",
                message="Recovered formulas differ noticeably from the reviewed reference formulas.",
                count=sum(1 for score in best_scores if score < 0.85),
            )
        )

    if fragmented_count:
        diagnostics.append(
            FormulaReferenceDiagnostic(
                code="reference_formula_fragmented_tokens",
                severity="warning",
                message="Recovered formulas still contain OCR-style token fragmentation.",
                count=fragmented_count,
            )
        )

    status = _derive_formula_reference_status(
        candidate_formula_count=candidate_formula_count,
        formula_recall=formula_recall,
        average_similarity=average_similarity,
        fragmented_count=fragmented_count,
    )
    return FormulaReferenceReport(
        status=status,
        reference_formula_count=reference_formula_count,
        candidate_formula_count=candidate_formula_count,
        matched_formula_count=matched_formula_count,
        missing_formula_count=missing_formula_count,
        extra_formula_count=extra_formula_count,
        fragmented_candidate_formula_count=fragmented_count,
        formula_recall=formula_recall,
        average_similarity=average_similarity,
        diagnostics=diagnostics,
    )


def _normalize_math_segment(segment: str) -> str:
    content = _strip_math_delimiters(segment).replace("\r", "\n")
    content = content.replace("−", "-").replace("×", r"\times")
    content = SPACING_COMMAND_RE.sub(" ", content)
    content = ENVIRONMENT_RE.sub(" ", content)
    content = content.replace("\\\\", " ")

    previous = None
    while previous != content:
        previous = content
        content = WRAPPER_COMMAND_RE.sub(r"\1", content)

    content = content.replace("\\%", "%").replace("\\_", "_")
    content = content.replace("{", " ").replace("}", " ")
    content = re.sub(r"\s+", "", content)
    return content.lower()


def _strip_math_delimiters(segment: str) -> str:
    stripped = segment.strip()
    if stripped.startswith("```"):
        match = FENCE_WRAPPER_RE.match(stripped)
        if match:
            return match.group("body")
    if stripped.startswith("$$") and stripped.endswith("$$"):
        return stripped[2:-2]
    if stripped.startswith(r"\[") and stripped.endswith(r"\]"):
        return stripped[2:-2]
    if stripped.startswith(r"\(") and stripped.endswith(r"\)"):
        return stripped[2:-2]
    if stripped.startswith("$") and stripped.endswith("$"):
        return stripped[1:-1]
    return stripped


def _derive_formula_reference_status(
    *,
    candidate_formula_count: int,
    formula_recall: float,
    average_similarity: float,
    fragmented_count: int,
) -> str:
    if candidate_formula_count == 0 or formula_recall < 0.5:
        return "poor"
    if formula_recall < 0.85 or average_similarity < 0.85 or fragmented_count:
        return "review"
    return "good"
