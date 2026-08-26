import pytest

from competitor_agent import CompetitorAgentConfigError, analyze_positioning, build_competitor_brief


def test_empty_competitor_list_blocks_analysis_instead_of_fabricating():
    result = build_competitor_brief("서초김치찌개", "한식 맛집", [])
    assert "블로킹" in result["status"]
    assert "지어내지" in result["reason"]


def test_none_competitor_list_also_blocks():
    result = build_competitor_brief("서초김치찌개", "한식 맛집", None)
    assert "블로킹" in result["status"]


def test_known_competitors_produce_analyzable_brief():
    competitors = [{"name": "옆집 김치찌개", "strength": "가격이 더 쌈", "weakness": "주차 공간 없음"}]
    result = build_competitor_brief("서초김치찌개", "한식 맛집", competitors)
    assert result["status"] == "분석 가능"
    assert result["competitor_names"] == ["옆집 김치찌개"]


def test_analyze_positioning_refuses_empty_list():
    with pytest.raises(CompetitorAgentConfigError):
        analyze_positioning("서초김치찌개", "한식 맛집", [])


def test_analyze_positioning_missing_api_key_raises_clean_error(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    competitors = [{"name": "옆집 김치찌개", "strength": "가격이 더 쌈", "weakness": "주차 공간 없음"}]
    with pytest.raises(CompetitorAgentConfigError):
        analyze_positioning("서초김치찌개", "한식 맛집", competitors)
