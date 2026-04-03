"""Generate a deterministic real PDF fixture for smoke tests."""
from __future__ import annotations

from pathlib import Path


LINES = [
    "doc_to_md smoke PDF",
    "This is a real PDF fixture for API and pipeline smoke tests.",
    "It is used to verify JSON and multipart inline conversion flows.",
    "Formula text sample: MC = A + B.",
]


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(lines: list[str]) -> bytes:
    content_lines = [
        "BT",
        "/F1 14 Tf",
        "72 740 Td",
        "18 TL",
    ]
    for index, line in enumerate(lines):
        escaped = _escape_pdf_text(line)
        if index == 0:
            content_lines.append(f"({escaped}) Tj")
        else:
            content_lines.extend(["T*", f"({escaped}) Tj"])
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("utf-8")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    chunks = [header]
    offsets = [0]
    current_offset = len(header)

    for index, body in enumerate(objects, start=1):
        obj = f"{index} 0 obj\n".encode("ascii") + body + b"\nendobj\n"
        offsets.append(current_offset)
        chunks.append(obj)
        current_offset += len(obj)

    xref_offset = current_offset
    xref_lines = [f"xref\n0 {len(objects) + 1}\n".encode("ascii"), b"0000000000 65535 f \n"]
    for offset in offsets[1:]:
        xref_lines.append(f"{offset:010d} 00000 n \n".encode("ascii"))

    trailer = (
        b"trailer\n"
        + f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode("ascii")
        + b"startxref\n"
        + str(xref_offset).encode("ascii")
        + b"\n%%EOF\n"
    )
    return b"".join(chunks + xref_lines + [trailer])


def main() -> int:
    target = Path("tests/fixtures/real_smoke.pdf")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(build_pdf(LINES))
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
