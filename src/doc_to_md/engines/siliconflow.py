"""SiliconFlow/DeepSeek engine implemented via the OpenAI-compatible API."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, List, Sequence, TypeVar

from openai import OpenAI

from config.settings import get_settings
from doc_to_md.pipeline.text_extraction import extract_text
from doc_to_md.utils.tokens import split_by_tokens
from .base import Engine, EngineResponse

T = TypeVar("T")


class SiliconFlowEngine(Engine):
    """Send extracted text to SiliconFlow's OpenAI-compatible chat completions API."""

    name = "siliconflow"

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        if not settings.siliconflow_api_key:
            raise RuntimeError("SILICONFLOW_API_KEY missing")
        self.api_key = settings.siliconflow_api_key
        self.model = model or settings.siliconflow_default_model
        self.client = OpenAI(api_key=self.api_key, base_url=settings.siliconflow_base_url)
        self.timeout = settings.siliconflow_timeout_seconds
        self.retry_attempts = settings.siliconflow_retry_attempts
        self.max_tokens = settings.siliconflow_max_input_tokens
        self.chunk_overlap = settings.siliconflow_chunk_overlap_tokens
        self._retry_backoff = 1.5

    def convert(self, path: Path) -> EngineResponse:  # pragma: no cover - network call
        raw_text = extract_text(path)
        chunks = self._chunk_text(raw_text)
        markdown_parts: list[str] = []

        for index, chunk in enumerate(chunks, start=1):
            user_prompt = self._build_user_prompt(path.name, chunk, index, len(chunks))
            completion = self._request_with_retry(
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a meticulous technical writer. Convert provided source text into clean Markdown, "
                                "preserving headings, tables, and lists."
                            ),
                        },
                        {"role": "user", "content": user_prompt},
                    ],
                    timeout=self.timeout,
                ),
                operation=f"siliconflow_chunk_{index}",
            )
            markdown_parts.append(self._extract_content(completion))

        markdown = self._compose_markdown(path.name, markdown_parts, len(chunks))
        return EngineResponse(markdown=markdown, model=self.model)

    def _chunk_text(self, text: str) -> List[str]:
        sanitized = text.strip()
        if not sanitized:
            return [sanitized]
        return split_by_tokens(
            sanitized,
            max_tokens=self.max_tokens,
            overlap_tokens=self.chunk_overlap,
        )

    def _build_user_prompt(self, filename: str, text: str, chunk_index: int, chunk_total: int) -> str:
        chunk_context = ""
        if chunk_total > 1:
            chunk_context = (
                f"This is chunk {chunk_index} of {chunk_total} extracted from '{filename}'. "
                "Maintain heading continuity across chunks and avoid duplicating intros already provided.\n\n"
            )

        return (
            f"{chunk_context}"
            f"Source document: {filename}\n\n"
            "Convert the following content into Markdown. Maintain hierarchical headings if obvious, convert numbered "
            "lists, and format tables when the structure is clear.\n\n"
            f"{text}"
        )

    def _compose_markdown(self, filename: str, parts: Sequence[str], chunk_total: int) -> str:
        cleaned_parts = [part.strip() for part in parts if part and part.strip()]
        body = "\n\n".join(cleaned_parts) if cleaned_parts else "_No content returned by SiliconFlow._"
        if chunk_total <= 1:
            return body
        notice = (
            f"_Note: Source document '{filename}' exceeded token limits and was processed "
            f"in {chunk_total} stitched chunks._"
        )
        return f"{notice}\n\n{body}"

    def _extract_content(self, completion) -> str:
        """Normalize OpenAI responses into a Markdown string."""
        if not completion.choices:
            raise RuntimeError("SiliconFlow response did not contain any choices")

        content = completion.choices[0].message.content
        if isinstance(content, str):
            return content.strip()
        raise RuntimeError(f"Unexpected content type in SiliconFlow response: {type(content)}")

    def _request_with_retry(self, func: Callable[[], T], operation: str) -> T:
        delay = self._retry_backoff
        last_exc: Exception | None = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                return func()
            except Exception as exc:  # noqa: BLE001 - bubble after retries
                last_exc = exc
                if attempt == self.retry_attempts:
                    break
                time.sleep(delay)
                delay *= 2
        assert last_exc is not None
        raise RuntimeError(f"Operation '{operation}' failed after {self.retry_attempts} attempts") from last_exc
