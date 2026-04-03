"""FastAPI router for the conversion app."""
from __future__ import annotations

import base64
import mimetypes

from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError
from starlette.datastructures import UploadFile as StarletteUploadFile

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


def _coerce_optional_bool(value: object, *, field_name: str) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "":
            return None
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
    raise HTTPException(
        status_code=422,
        detail=[
            {
                "loc": ["body", field_name],
                "msg": "Input should be a valid boolean",
                "type": "bool_parsing",
            }
        ],
    )


def _coerce_optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


async def _parse_inline_request(request: Request) -> InlineConvertRequest:
    content_type = request.headers.get("content-type", "").lower()
    if "multipart/form-data" in content_type:
        try:
            form = await request.form()
        except (AssertionError, RuntimeError) as exc:
            raise HTTPException(
                status_code=500,
                detail="Multipart support requires `python-multipart`. Install it with `pip install \\\".[api]\\\"`.",
            ) from exc

        upload = form.get("file")
        if not isinstance(upload, StarletteUploadFile):
            raise HTTPException(status_code=422, detail=[{"loc": ["body", "file"], "msg": "Field required", "type": "missing"}])

        source_name = _coerce_optional_text(form.get("source_name")) or upload.filename
        if not source_name:
            raise HTTPException(
                status_code=422,
                detail=[{"loc": ["body", "source_name"], "msg": "source_name is required when upload filename is missing", "type": "missing"}],
            )

        payload = {
            "source_name": source_name,
            "content_base64": base64.b64encode(await upload.read()).decode("ascii"),
            "engine": _coerce_optional_text(form.get("engine")),
            "model": _coerce_optional_text(form.get("model")),
            "no_page_info": _coerce_optional_bool(form.get("no_page_info"), field_name="no_page_info") or False,
            "formula_ocr_enabled": _coerce_optional_bool(form.get("formula_ocr_enabled"), field_name="formula_ocr_enabled"),
            "formula_ocr_provider": _coerce_optional_text(form.get("formula_ocr_provider")),
            "include_assets": _coerce_optional_bool(form.get("include_assets"), field_name="include_assets") or False,
        }
        try:
            return InlineConvertRequest.model_validate(payload)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=exc.errors()) from exc

    if content_type.startswith("application/json") or not content_type:
        try:
            payload = await request.json()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc
        try:
            return InlineConvertRequest.model_validate(payload)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=exc.errors()) from exc

    raise HTTPException(
        status_code=415,
        detail="Unsupported content type. Use application/json or multipart/form-data.",
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
async def convert_inline(request: Request) -> InlineConvertResponse:
    payload = await _parse_inline_request(request)
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
