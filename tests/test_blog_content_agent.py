import pytest

from blog_content_agent import build_blog_draft, render_markdown
from content_playbook import HEADLINE_FORMULAS


def test_empty_keywords_raises():
    with pytest.raises(ValueError):
        build_blog_draft("업체", "카테고리", [])


def test_title_candidates_use_all_headline_formulas():
    draft = build_blog_draft("예시병원", "정형외과", ["무릎 통증 원인"], "강남")
    assert len(draft["title_candidates"]) == len(HEADLINE_FORMULAS)
    # 밋밋한 옛날 템플릿("완벽 가이드 |")으로 퇴행하지 않았는지 확인
    assert not any("완벽 가이드 |" in t for t in draft["title_candidates"])


def test_works_without_location():
    draft = build_blog_draft("예시병원", "정형외과", ["무릎 통증 원인"])
    assert all(draft["title_candidates"])
    assert "  " not in draft["title_candidates"][1]  # location 없을 때 중복 공백 없는지


def test_customer_stage_passthrough():
    draft = build_blog_draft("업체", "카테고리", ["키워드"], customer_stage="decision")
    assert draft["customer_stage"] == "decision"


def test_render_markdown_contains_all_keywords():
    draft = build_blog_draft("업체", "카테고리", ["키워드1", "키워드2"])
    md = render_markdown(draft)
    assert "키워드1" in md and "키워드2" in md
    assert draft["cta"] in md
