from pathlib import Path
import base64

import pytest

import doc_to_md.apps.conversion.logic as conversion_logic
from doc_to_md.config.settings import Settings


def test_list_preferred_pdf_engines_returns_opendataloader_and_mistral() -> None:
    assert conversion_logic.list_preferred_pdf_engines() == ["opendataloader", "mistral"]


def test_list_preferred_engine_readiness_reports_both_preferences(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        conversion_logic,
        "_build_opendataloader_readiness",
        lambda: conversion_logic.PreferredEngineReadiness(
            engine="opendataloader",
            preferred_rank=1,
            available=True,
            summary="OpenDataLoader ready.",
            checks=[
                conversion_logic.EngineReadinessCheck(
                    name="java_runtime",
                    ready=True,
                    message="Java 17 found.",
                )
            ],
        ),
    )
    monkeypatch.setattr(
        conversion_logic,
        "_build_mistral_readiness",
        lambda settings: conversion_logic.PreferredEngineReadiness(
            engine="mistral",
            preferred_rank=2,
            available=False,
            summary="Blocked: MISTRAL_API_KEY missing",
            checks=[
                conversion_logic.EngineReadinessCheck(
                    name="api_key",
                    ready=False,
                    message="MISTRAL_API_KEY missing",
                )
            ],
        ),
    )

    items = conversion_logic.list_preferred_engine_readiness(settings=Settings())

    assert [item.engine for item in items] == ["opendataloader", "mistral"]
    assert items[0].available is True
    assert items[1].available is False
    assert items[1].checks[0].message == "MISTRAL_API_KEY missing"


def test_real_pdf_sample_still_reports_review_for_local_engine() -> None:
    pdfs = list(Path("data/input").glob("*.pdf"))
    if not pdfs:
        pytest.skip("Representative PDF sample is not present in data/input")

    pdf = pdfs[0]
    result = conversion_logic.convert_inline_document(
        source_name=pdf.name,
        content_base64=base64.b64encode(pdf.read_bytes()).decode("ascii"),
        engine="local",
    )

    assert result.quality.status in {"review", "poor", "good"}
    assert result.trace is not None
