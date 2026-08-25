from business_dna import build_business_dna, classify_business


def test_classify_restaurant():
    assert classify_business("고깃집") == "restaurant"
    assert classify_business("한식 맛집") == "restaurant"


def test_classify_labor_firm():
    assert classify_business("노무법인") == "labor_firm"


def test_classify_dental():
    assert classify_business("치과") == "dental"


def test_classify_unknown_falls_back_to_generic():
    assert classify_business("애견호텔") == "generic"


def test_stage6_prep_verticals_classify_correctly_but_stay_inactive():
    # 6단계(업종 확장) 대비 미리 등록한 프로필들 — 전부 아직 비활성이어야 한다
    for category, expected_vertical in [
        ("정형외과", "medical_general"),
        ("미용실", "beauty"),
        ("입시학원", "academy"),
        ("법무법인", "legal_tax"),
    ]:
        assert classify_business(category) == expected_vertical
        dna = build_business_dna("업체", category)
        assert dna["vertical_active"] is False, f"{expected_vertical}은 아직 활성화하면 안 됨"


def test_dental_is_inactive_by_default():
    dna = build_business_dna("예시치과", "치과")
    assert dna["vertical_active"] is False
    assert dna["banned_terms"]  # 사전 정의 금지어가 채워져 있어야 함


def test_restaurant_is_active_and_allows_performance_pricing():
    dna = build_business_dna("예시식당", "고깃집")
    assert dna["vertical_active"] is True
    assert dna["performance_pricing_allowed"] is True


def test_labor_firm_disallows_performance_pricing():
    dna = build_business_dna("예시노무법인", "노무법인")
    assert dna["performance_pricing_allowed"] is False


def test_explicit_banned_terms_merge_without_duplicating_profile_defaults():
    dna = build_business_dna("예시노무법인", "노무법인", explicit_banned_terms=["고객 연결해드립니다", "새 표현"])
    assert dna["banned_terms"].count("고객 연결해드립니다") == 1
    assert "새 표현" in dna["banned_terms"]
