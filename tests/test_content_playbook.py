from content_playbook import build_playbook_instructions, pick_headline_formula, render_headline


def test_pick_headline_formula_maps_all_known_stages():
    for stage in ("awareness", "comparison", "decision"):
        formula = pick_headline_formula(stage)
        assert "template" in formula and "name" in formula


def test_pick_headline_formula_unknown_stage_falls_back():
    formula = pick_headline_formula("nonsense")
    assert formula == pick_headline_formula("awareness")


def test_render_headline_no_double_spaces_without_location():
    formula = pick_headline_formula("comparison")  # "{category} 선택 전..." 형: location 안 씀
    title = render_headline(formula, "키워드", "카테고리", location=None, number=3)
    assert "  " not in title


def test_render_headline_fills_all_fields():
    formula = {"template": "{location}{category} {keyword} {number}"}
    title = render_headline(formula, "키워드", "카테고리", "강남", number=5)
    assert title == "강남 카테고리 키워드 5"


def test_build_playbook_instructions_has_all_sections():
    text = build_playbook_instructions("awareness")
    assert "헤드라인" in text
    assert "네이버 SEO" in text
    assert "전환 심리학" in text
