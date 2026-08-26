from company_core import build_company_profile, render_summary


def test_build_company_profile_backward_compatible_with_minimal_client():
    # 기존 clients/example-restaurant.json 수준의 최소 필드만 있어도 깨지지 않아야 한다
    client = {
        "slug": "example-restaurant",
        "business_name": "예시식당",
        "category": "고깃집",
        "location": "강남",
        "keywords": ["강남 회식"],
        "review_target_phone": "010-0000-0000",
        "ga4_property_id": None,
    }
    profile = build_company_profile(client)
    assert profile["company_id"] == "example-restaurant"
    assert profile["business_dna"]["vertical"] == "restaurant"
    assert profile["business_dna"]["vertical_active"] is True
    assert profile["growth_profile"]["revenue"] is None
    assert profile["growth_profile"]["revenue_gap"] is None


def test_build_company_profile_fills_new_fields_when_present():
    client = {
        "slug": "test-biz",
        "business_name": "테스트업체",
        "category": "고깃집",
        "homepage": "https://example.com",
        "revenue": 30000000,
        "target_revenue": 50000000,
        "employee_count": 5,
        "ad_budget": 1000000,
    }
    profile = build_company_profile(client)
    assert profile["business_profile"]["homepage"] == "https://example.com"
    assert profile["business_profile"]["employee_count"] == 5
    assert profile["marketing_profile"]["ad_budget"] == 1000000
    assert profile["growth_profile"]["revenue_gap"] == 20000000


def test_goal_decomposition_absent_without_revenue_gap():
    client = {"slug": "example-restaurant", "business_name": "예시식당", "category": "고깃집"}
    profile = build_company_profile(client)
    assert profile["growth_profile"]["goal_decomposition"] is None


def test_goal_decomposition_flags_missing_funnel_rates():
    client = {
        "slug": "test-biz",
        "business_name": "테스트업체",
        "category": "고깃집",
        "revenue": 10_000_000,
        "target_revenue": 20_000_000,
    }
    profile = build_company_profile(client)
    decomposition = profile["growth_profile"]["goal_decomposition"]
    assert decomposition["status"] == "데이터 부족"


def test_goal_decomposition_computes_when_funnel_rates_provided():
    client = {
        "slug": "test-biz",
        "business_name": "테스트업체",
        "category": "고깃집",
        "revenue": 10_000_000,
        "target_revenue": 40_000_000,
        "funnel_rates": {"avg_order_value": 30_000, "visit_conversion_rate": 0.5},
    }
    profile = build_company_profile(client)
    decomposition = profile["growth_profile"]["goal_decomposition"]
    assert decomposition["status"] == "계산 완료"
    assert decomposition["required_top_of_funnel"] > 0


def test_dental_vertical_stays_blocked_through_company_core():
    client = {"slug": "example-dental", "business_name": "예시치과", "category": "치과"}
    profile = build_company_profile(client)
    assert profile["business_dna"]["vertical_active"] is False


def test_render_summary_includes_business_name_and_vertical_status():
    client = {"slug": "example-restaurant", "business_name": "예시식당", "category": "고깃집", "location": "강남"}
    profile = build_company_profile(client)
    summary = render_summary(profile)
    assert "예시식당" in summary
    assert "활성" in summary


def test_render_summary_handles_missing_revenue_gracefully():
    client = {"slug": "example-dental", "business_name": "예시치과", "category": "치과"}
    profile = build_company_profile(client)
    summary = render_summary(profile)
    assert "매출" not in summary  # revenue/target_revenue 둘 다 없으면 그 줄을 아예 안 보여줌
