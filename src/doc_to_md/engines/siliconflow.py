"""SiliconFlow/DeepSeek engine implemented via the OpenAI-compatible API."""
from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from openai import OpenAI

from config.settings import get_settings
from doc_to_md.pipeline.text_extraction import extract_text
from .base import Engine, EngineResponse


class SiliconFlowEngine(Engine):
    """Send extracted text to SiliconFlow's OpenAI-compatible chat completions API."""

    name = "siliconflow"
    _MAX_INPUT_CHARS = 30_000

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        if not settings.siliconflow_api_key:
            raise RuntimeError("SILICONFLOW_API_KEY missing")
        self.api_key = settings.siliconflow_api_key
        self.model = model or settings.siliconflow_default_model
        self.client = OpenAI(api_key=self.api_key, base_url=settings.siliconflow_base_url)

    def convert(self, path: Path) -> EngineResponse:  # pragma: no cover - network call
        raw_text = extract_text(path)
        payload_text, truncated = self._truncate(raw_text)
        user_prompt = self._build_user_prompt(path.name, payload_text, truncated)

        completion = self.client.chat.completions.create(
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
        )

        markdown = self._extract_content(completion)
        return EngineResponse(markdown=markdown, model=self.model)

    def _truncate(self, text: str) -> tuple[str, bool]:
        if len(text) <= self._MAX_INPUT_CHARS:
            return text, False
        snippet = text[: self._MAX_INPUT_CHARS]
        return f"{snippet}\n\n[Truncated due to length]", True

    def _build_user_prompt(self, filename: str, text: str, truncated: bool) -> str:
        notice = (
            "The source text was truncated to fit token limits. Summaries should mention that sections may be missing.\n\n"
            if truncated
            else ""
        )
        return (
            f"{notice}"
            f"Source document: {filename}\n\n"
            "Convert the following content into Markdown. Maintain hierarchical headings if obvious, convert numbered "
            "lists, and format tables when the structure is clear.\n\n"
            f"{text}"
        )

    def _extract_content(self, completion) -> str:
        """Normalize OpenAI responses into a Markdown string."""
        if not completion.choices:
            raise RuntimeError("SiliconFlow response did not contain any choices")

        content = completion.choices[0].message.content
        if isinstance(content, str):
            return content.strip()
        raise RuntimeError(f"Unexpected content type in SiliconFlow response: {type(content)}")
