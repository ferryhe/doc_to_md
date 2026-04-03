"""FastAPI router for the conversion app."""
from __future__ import annotations

import base64
import mimetypes

from fastapi import APIRouter, HTTPException

from doc_to_md.apps.conversion.logic import convert_inline_document, list_engine_names, run_conversion
from doc_to_md.apps.conversion.schemas import (
    ConvertRequest,
    ConvertResponse,
    DocumentResultResponse,
    EnginesResponse,
    HealthResponse,
    InlineAssetResponse,
    InlineConvertRequest,
    InlineConvertResponse,
    MarkdownDiagnosticResponse,
    MarkdownQualityResponse,
    PostprocessTraceResponse,
)

router = APIRouter(prefix="/apps/conversion", tags=["conversion"])


def _build_quality_response(quality) -> MarkdownQualityResponse | None:
    if quality is None:
        return None
    return MarkdownQualityResponse(
        status=quality.status,
        formula_status=quality.formula_status,
        headings=quality.headings,
        bullet_lines=quality.bullet_lines,
        table_lines=quality.table_lines,
        image_references=quality.image_references,
        formula_image_references=quality.formula_image_references,
        inline_math_segments=quality.inline_math_segments,
        block_math_segments=quality.block_math_segments,
        diagnostics=[
            MarkdownDiagnosticResponse(
                code=diagnostic.code,
                severity=diagnostic.severity,
                message=diagnostic.message,
                count=diagnostic.count,
            )
            for diagnostic in quality.diagnostics
        ],
    )


def _build_trace_response(trace) -> PostprocessTraceResponse | None:
    if trace is None:
        return None
    return PostprocessTraceResponse(
        math_normalization_changed=trace.math_normalization_changed,
        formula_ocr_enabled=trace.formula_ocr_enabled,
        formula_ocr_provider=trace.formula_ocr_provider,
        formula_ocr_attempted=trace.formula_ocr_attempted,
        formula_ocr_applied=trace.formula_ocr_applied,
        formula_image_references_before=trace.formula_image_references_before,
        formula_image_references_after=trace.formula_image_references_after,
        asset_count_before=trace.asset_count_before,
        asset_count_after=trace.asset_count_after,
        postprocess_changed=trace.postprocess_changed,
    )


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@router.get("/engines", response_model=EnginesResponse)
def list_engines() -> EnginesResponse:
    return EnginesResponse(engines=list_engine_names())


@router.post("/convert", response_model=ConvertResponse)
def convert_documents(payload: ConvertRequest) -> ConvertResponse:
    try:
        summary = run_conversion(
            input_path=payload.input_path,
            output_path=payload.output_path,
            engine=payload.engine,
            model=payload.model,
            since=payload.since,
            no_page_info=payload.no_page_info,
            dry_run=payload.dry_run,
            formula_ocr_enabled=payload.formula_ocr_enabled,
            formula_ocr_provider=payload.formula_ocr_provider,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ConvertResponse(
        engine=summary.engine,
        model=summary.model,
        input_dir=str(summary.input_dir),
        output_dir=str(summary.output_dir),
        total_candidates=summary.metrics.total_candidates,
        eligible=summary.metrics.eligible,
        converted=summary.metrics.successes,
        failed=summary.metrics.failures,
        skipped_since=summary.metrics.skipped_by_since,
        dry_run=summary.metrics.dry_run,
        duration_seconds=summary.duration_seconds,
        results=[
            DocumentResultResponse(
                source_path=str(item.source_path),
                status=item.status,
                output_path=str(item.output_path) if item.output_path else None,
                error=item.error,
                modified_at=item.modified_at,
                quality=_build_quality_response(item.quality),
                trace=_build_trace_response(item.trace),
            )
            for item in summary.results
        ],
    )


@router.post("/convert-inline", response_model=InlineConvertResponse)
def convert_inline(payload: InlineConvertRequest) -> InlineConvertResponse:
    try:
        result = convert_inline_document(
            source_name=payload.source_name,
            content_base64=payload.content_base64,
            engine=payload.engine,
            model=payload.model,
            no_page_info=payload.no_page_info,
            formula_ocr_enabled=payload.formula_ocr_enabled,
            formula_ocr_provider=payload.formula_ocr_provider,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return InlineConvertResponse(
        source_name=result.source_name,
        engine=result.engine,
        model=result.model,
        markdown=result.markdown,
        quality=_build_quality_response(result.quality),
        trace=_build_trace_response(result.trace),
        asset_count=len(result.assets),
        assets=[
            InlineAssetResponse(
                filename=asset.filename,
                subdir=asset.subdir,
                media_type=mimetypes.guess_type(asset.filename)[0],
                content_base64=base64.b64encode(asset.data).decode("ascii") if payload.include_assets else None,
            )
            for asset in result.assets
        ],
        duration_seconds=result.duration_seconds,
    )
