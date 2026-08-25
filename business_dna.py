"""Business DNA / Industry AI — 업체 정보를 보고 업종을 판별해 기본 프로필을 채운다.

정직하게 말하면 "AI가 알아서 판단"이 아니라 **카테고리 문자열 매칭 + 업종별
사전 정의 프로필 룩업**이다. 지금 지원 업종은 3개(음식점/노무법인/치과)뿐이고,
고객사가 늘어야 이 매칭 로직을 정교화할 데이터가 생긴다 (docs/north-star-vision.md 3절).

실제로 하는 일: `clients/*.json`을 쓸 때 banned_terms·과금방식 제약을 매번 손으로
넣지 않아도, 카테고리만 봐도 업종별 기본값(금지어, 성과연동 가격 허용 여부,
컴플라이언스 메모)을 자동으로 채워준다. 치과처럼 의도적으로 보류한 버티컬은
`active: False`로 막아둬서, 실수로 콘텐츠를 만들어버리는 걸 코드 레벨에서 방지한다.
"""

VERTICAL_PROFILES = {
    "restaurant": {
        "match_keywords": ["식당", "고깃집", "음식점", "카페", "레스토랑", "술집", "포차", "맛집"],
        "banned_terms": [],
        "performance_pricing_allowed": True,
        "default_customer_stage": "comparison",
        "compliance_note": "식품위생법상 표시·광고 기본 규정만 확인해도 충분",
        "active": True,
    },
    "labor_firm": {
        "match_keywords": ["노무", "노무법인", "노무사"],
        "banned_terms": ["고객 연결해드립니다", "상담하시면 소개", "성사 시 정산"],
        "performance_pricing_allowed": False,
        "default_customer_stage": "awareness",
        "compliance_note": "공인노무사법 제27조의2(확인 완료) — 정액/광고비 비례만, 문의·수임 성사 연동 금지",
        "active": True,
    },
    "dental": {
        "match_keywords": ["치과", "임플란트", "치아교정", "충치"],
        "banned_terms": ["100% 완치", "무통증 시술", "안전성 보장", "타 병원보다 우수", "환자 치료 후기"],
        "performance_pricing_allowed": False,
        "default_customer_stage": "decision",
        "compliance_note": "의료법 의료광고 규제 — 조문 미검증. Phase 3까지 의도적으로 비활성",
        "active": False,
    },
}


def classify_business(category: str) -> str:
    """카테고리 문자열을 보고 버티컬 키를 반환한다. 매칭 안 되면 'generic'."""

    for vertical, profile in VERTICAL_PROFILES.items():
        if any(kw in category for kw in profile["match_keywords"]):
            return vertical
    return "generic"


def build_business_dna(business_name: str, category: str, explicit_banned_terms: list[str] | None = None) -> dict:
    """업종 기본값을 채운 DNA를 반환한다. explicit_banned_terms는 프로필 기본값에 병합된다."""

    vertical = classify_business(category)
    profile = VERTICAL_PROFILES.get(vertical, {})

    banned = list(profile.get("banned_terms", []))
    for term in explicit_banned_terms or []:
        if term not in banned:
            banned.append(term)

    return {
        "business_name": business_name,
        "vertical": vertical,
        "vertical_active": profile.get("active", True),
        "banned_terms": banned,
        "performance_pricing_allowed": profile.get("performance_pricing_allowed", True),
        "default_customer_stage": profile.get("default_customer_stage", "awareness"),
        "compliance_note": profile.get("compliance_note", "일반 업종 — 특이 규제 없음, 그래도 표시광고법 기본은 확인"),
    }


def main():
    for name, category in [("예시식당", "고깃집"), ("예시노무법인", "노무법인"), ("예시치과", "치과"), ("예시학원", "입시학원")]:
        dna = build_business_dna(name, category)
        print(f"{name} ({category}) -> {dna}")


if __name__ == "__main__":
    main()
