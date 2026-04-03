from doc_to_md.quality import evaluate_markdown_quality


def test_quality_report_marks_formula_images_as_poor() -> None:
    markdown = "计算公式如下：\n\n![image 1](sample_images/imageFile1.png)\n"

    report = evaluate_markdown_quality(markdown)

    assert report.status == "poor"
    assert report.formula_status == "poor"
    assert report.formula_image_references == 1
    assert report.diagnostics[0].code == "formula_image_reference"


def test_quality_report_marks_clean_formula_output_as_good() -> None:
    markdown = "# Result\n\n$$MC = A + B$$\n\n|相关系数|$MC_{非寿险保险}$|1|"

    report = evaluate_markdown_quality(markdown)

    assert report.status == "good"
    assert report.formula_status == "good"
    assert report.block_math_segments == 1
    assert report.inline_math_segments == 1
    assert report.formula_image_references == 0


def test_quality_report_marks_formula_context_without_math_for_review() -> None:
    markdown = "计算公式如下：\n\n最低资本由多个因子组成。\n"

    report = evaluate_markdown_quality(markdown)

    assert report.status == "review"
    assert report.formula_status == "review"
    assert any(item.code == "formula_context_without_math" for item in report.diagnostics)


def test_quality_report_counts_fenced_math_blocks() -> None:
    markdown = "计算公式如下：\n\n```math\nMC = EX \\times RF\n```\n"

    report = evaluate_markdown_quality(markdown)

    assert report.status == "good"
    assert report.formula_status == "good"
    assert report.block_math_segments == 1
