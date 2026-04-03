"""Post-processing helpers after engine response."""
from __future__ import annotations

from dataclasses import dataclass
import html
import re

from doc_to_md.config.settings import Settings, get_settings
from doc_to_md.engines.base import EngineAsset
from doc_to_md.pipeline.formula_ocr import replace_formula_images
from doc_to_md.quality import MarkdownQualityReport, evaluate_markdown_quality


@dataclass(slots=True)
class ConversionResult:
    source_name: str
    markdown: str
    engine: str
    assets: list[EngineAsset]


@dataclass(slots=True)
class PostprocessTrace:
    math_normalization_changed: bool
    formula_ocr_enabled: bool
    formula_ocr_provider: str | None
    formula_ocr_attempted: bool
    formula_ocr_applied: bool
    formula_image_references_before: int
    formula_image_references_after: int
    asset_count_before: int
    asset_count_after: int
    postprocess_changed: bool


@dataclass(slots=True)
class PostprocessOutcome:
    result: ConversionResult
    quality: MarkdownQualityReport
    trace: PostprocessTrace


MATH_SEGMENT_PATTERN = re.compile(
    r"(?P<display_dollar>\$\$.*?\$\$)"
    r"|(?P<display_bracket>\\\[.*?\\\])"
    r"|(?P<inline_paren>\\\(.*?\\\))"
    r"|(?P<inline_dollar>(?<!\$)\$(?!\$).*?(?<!\\)\$)",
    re.DOTALL,
)

ENTITY_REPLACEMENTS = (
    (re.compile(r"&\s*lt;", re.IGNORECASE), "<"),
    (re.compile(r"&\s*gt;", re.IGNORECASE), ">"),
    (re.compile(r"&\s*amp;", re.IGNORECASE), "&"),
)

MATH_OPERATOR_SPACING_PATTERN = re.compile(r"(?<!\\)[ \t]*([_^])[ \t]*")

BROKEN_CJK_SUBSUP_WITH_INDEX_PATTERN = re.compile(
    r"(?P<op>[_^])\s*\{\s*\\(?P<label>[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+)\s*_(?P<index>[A-Za-z0-9]+)\s*\}"
)

BROKEN_CJK_SUBSUP_PATTERN = re.compile(
    r"(?P<op>[_^])\s*\{\s*\\(?P<label>[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+)\s*\}"
)


def postprocess_conversion_result(
    result: ConversionResult,
    *,
    settings: Settings | None = None,
) -> PostprocessOutcome:
    cleaned = result.markdown.strip()
    normalized = ConversionResult(
        source_name=result.source_name,
        markdown=normalize_math_entities(cleaned),
        engine=result.engine,
        assets=result.assets,
    )
    active_settings = settings or get_settings()
    quality_before = evaluate_markdown_quality(normalized.markdown)
    after_formula = normalized
    formula_ocr_attempted = active_settings.formula_ocr_enabled and quality_before.formula_image_references > 0

    if active_settings.formula_ocr_enabled:
        after_formula = replace_formula_images(normalized, settings=active_settings)

    final_result = ConversionResult(
        source_name=after_formula.source_name,
        markdown=normalize_math_entities(after_formula.markdown),
        engine=after_formula.engine,
        assets=after_formula.assets,
    )
    final_quality = evaluate_markdown_quality(final_result.markdown)
    formula_ocr_applied = formula_ocr_attempted and (
        final_result.markdown != normalized.markdown or len(final_result.assets) != len(normalized.assets)
    )
    trace = PostprocessTrace(
        math_normalization_changed=normalized.markdown != cleaned,
        formula_ocr_enabled=active_settings.formula_ocr_enabled,
        formula_ocr_provider=active_settings.formula_ocr_provider if active_settings.formula_ocr_enabled else None,
        formula_ocr_attempted=formula_ocr_attempted,
        formula_ocr_applied=formula_ocr_applied,
        formula_image_references_before=quality_before.formula_image_references,
        formula_image_references_after=final_quality.formula_image_references,
        asset_count_before=len(result.assets),
        asset_count_after=len(final_result.assets),
        postprocess_changed=final_result.markdown != result.markdown or len(final_result.assets) != len(result.assets),
    )
    return PostprocessOutcome(result=final_result, quality=final_quality, trace=trace)


def enforce_markdown(result: ConversionResult, *, settings: Settings | None = None) -> ConversionResult:
    """Normalize Markdown and optionally run formula OCR cleanup."""
    return postprocess_conversion_result(result, settings=settings).result


def normalize_math_entities(markdown: str) -> str:
    return MATH_SEGMENT_PATTERN.sub(lambda match: _decode_math_entities(match.group(0)), markdown)


def _decode_math_entities(segment: str) -> str:
    cleaned = segment
    for pattern, replacement in ENTITY_REPLACEMENTS:
        cleaned = pattern.sub(replacement, cleaned)
    for _ in range(3):
        unescaped = html.unescape(cleaned)
        if unescaped == cleaned:
            break
        cleaned = unescaped
    cleaned = BROKEN_CJK_SUBSUP_WITH_INDEX_PATTERN.sub(_replace_broken_cjk_subsup_with_index, cleaned)
    cleaned = BROKEN_CJK_SUBSUP_PATTERN.sub(_replace_broken_cjk_subsup, cleaned)
    cleaned = _normalize_math_operator_spacing(cleaned)
    return cleaned.replace("\xa0", " ")


def _normalize_math_operator_spacing(segment: str) -> str:
    return MATH_OPERATOR_SPACING_PATTERN.sub(r" \1 ", segment)


def _replace_broken_cjk_subsup_with_index(match: re.Match[str]) -> str:
    op = match.group("op")
    label = match.group("label")
    index = match.group("index")
    return f"{op}{{\\text{{{label}}}_{index}}}"


def _replace_broken_cjk_subsup(match: re.Match[str]) -> str:
    op = match.group("op")
    label = match.group("label")
    return f"{op}{{\\text{{{label}}}}}"
