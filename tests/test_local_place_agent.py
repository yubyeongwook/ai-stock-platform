from local_place_agent import build_intro_copy, build_local_marketing_plan


def test_intro_copy_leads_with_keyword():
    copy = build_intro_copy("예시병원", "정형외과", "강남")
    assert copy.startswith("강남 정형외과")


def test_intro_copy_without_benefit_has_no_extra_claim():
    copy = build_intro_copy("업체", "카테고리", "지역")
    assert "혜택" not in copy


def test_intro_copy_includes_benefit_only_when_given():
    copy = build_intro_copy("업체", "카테고리", "지역", first_visit_benefit="첫 방문 10% 할인")
    assert "첫 방문 10% 할인" in copy


def test_plan_has_single_cta_wording():
    plan = build_local_marketing_plan("업체", "카테고리", "지역")
    # 단일 CTA 원칙: 전화 하나만, 다른 채널을 나열하지 않는다
    assert plan["intro_copy"].count("전화") == 1


def test_checklist_uses_business_fields():
    plan = build_local_marketing_plan("예시식당", "고깃집", "강남")
    assert any("예시식당" in item for item in plan["checklist"])
