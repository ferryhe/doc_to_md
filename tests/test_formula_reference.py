from doc_to_md.formula_reference import evaluate_formula_reference


def test_formula_reference_marks_clean_match_as_good() -> None:
    reference = (
        "```math\n"
        "MC = EX \\times RF\n"
        "```\n\n"
        "```math\n"
        "k_1 = \\begin{cases} 0 & x \\le 1 \\\\ 1 & x > 1 \\end{cases}\n"
        "```\n"
    )
    candidate = (
        "$$\\mathrm{MC} = \\mathrm{EX} \\times \\mathrm{RF}$$\n\n"
        "$$k_1 = \\begin{cases}0 & x \\le 1 \\\\ 1 & x > 1\\end{cases}$$\n"
    )

    report = evaluate_formula_reference(candidate, reference)

    assert report.status == "good"
    assert report.reference_formula_count == 2
    assert report.candidate_formula_count == 2
    assert report.matched_formula_count == 2
    assert report.formula_recall == 1.0
    assert report.average_similarity >= 0.85


def test_formula_reference_marks_fragmented_match_for_review() -> None:
    reference = "```math\n0.148 = k_2\n```\n"
    candidate = "```math\n0. 1 4 8 = k_2\n```\n"

    report = evaluate_formula_reference(candidate, reference)

    assert report.status == "review"
    assert report.formula_recall == 1.0
    assert any(item.code == "reference_formula_fragmented_tokens" for item in report.diagnostics)


def test_formula_reference_marks_missing_explicit_math_as_poor() -> None:
    reference = "```math\nMC = EX \\times RF\n```\n"
    candidate = "计算公式如下：\nMC = EX × RF\n"

    report = evaluate_formula_reference(candidate, reference)

    assert report.status == "poor"
    assert report.candidate_formula_count == 0
    assert report.matched_formula_count == 0
    assert any(item.code == "reference_formula_missing_all" for item in report.diagnostics)
