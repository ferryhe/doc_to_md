from pathlib import Path

from doc_to_md.pipeline.loader import iter_documents


def test_iter_documents(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "b.bin").write_text("ignore", encoding="utf-8")
    files = list(iter_documents(tmp_path))
    assert len(files) == 1
    assert files[0].name == "a.txt"
