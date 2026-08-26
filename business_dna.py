"""Business DNA / Industry AI — 업체 정보를 보고 업종을 판별해 기본 프로필을 채운다.

정직하게 말하면 "AI가 알아서 판단"이 아니라 **카테고리 문자열 매칭 + 업종별
사전 정의 프로필 룩업**이다. 지금 지원 업종은 3개(음식점/노무법인/치과)뿐이고,
고객사가 늘어야 이 매칭 로직을 정교화할 데이터가 생긴다 (docs/north-star-vision.md 3절).

실제로 하는 일: `clients/*.json`을 쓸 때 banned_terms·과금방식 제약을 매번 손으로
넣지 않아도, 카테고리만 봐도 업종별 기본값(금지어, 성과연동 가격 허용 여부,
컴플라이언스 메모)을 자동으로 채워준다. 치과처럼 의도적으로 보류한 버티컬은
`active: False`로 막아둬서, 실수로 콘텐츠를 만들어버리는 걸 코드 레벨에서 방지한다.
"""

# AI Freedom Level — "AI가 이 업체에 대해 사람 개입 없이 얼마나 알아서 해도 되는가"를
# 0~5로 명시한다. 새 개념이 아니라, 이 코드베이스가 처음부터 지켜온 3단계 게이트
# (🟢자동 실행 / 🟡생성+승인 / 🔴사람 필수 — docs/ai-growth-os-architecture.md 4절)를
# 업종마다 다른 기본값으로 세분화해서 명시적인 숫자로 못박은 것뿐이다. 데이터로 계산한
# 점수가 아니라 컴플라이언스 판단에 따른 설정값이다.
FREEDOM_LEVELS = {
    0: "분석만 — 콘텐츠·액션 생성 자체를 안 함",
    1: "추천만 — 뭘 하면 좋을지 후보만 보여줌, 초안도 안 만듦",
    2: "초안 자동 생성 — 콘텐츠 초안까지는 자동, 발행은 항상 사람이 함",
    3: "승인 후 실행 — 초안+발행 준비까지 자동, 최종 발행 버튼만 사람",
    4: "저위험 자동 실행 — 블로그 등 저위험 채널은 자동 발행, 광고비·가격 등은 여전히 승인",
    5: "조건부 자율운영 — 사전에 합의한 범위·한도 내에서는 승인 없이 실행",
}

VERTICAL_PROFILES = {
    "restaurant": {
        "match_keywords": ["식당", "고깃집", "음식점", "카페", "레스토랑", "술집", "포차", "맛집"],
        "banned_terms": [],
        "performance_pricing_allowed": True,
        "default_customer_stage": "comparison",
        "compliance_note": "식품위생법상 표시·광고 기본 규정만 확인해도 충분",
        "active": True,
        "default_freedom_level": 3,
    },
    "labor_firm": {
        "match_keywords": ["노무", "노무법인", "노무사"],
        "banned_terms": ["고객 연결해드립니다", "상담하시면 소개", "성사 시 정산"],
        "performance_pricing_allowed": False,
        "default_customer_stage": "awareness",
        "compliance_note": "공인노무사법 제27조의2(확인 완료) — 정액/광고비 비례만, 문의·수임 성사 연동 금지",
        "active": True,
        "default_freedom_level": 2,
    },
    "dental": {
        "match_keywords": ["치과", "임플란트", "치아교정", "충치"],
        "banned_terms": ["100% 완치", "무통증 시술", "안전성 보장", "타 병원보다 우수", "환자 치료 후기"],
        "performance_pricing_allowed": False,
        "default_customer_stage": "decision",
        "compliance_note": "의료법 의료광고 규제 — 조문 미검증. Phase 3까지 의도적으로 비활성",
        "active": False,
        "default_freedom_level": 0,
    },
    # 아래는 6단계(업종 확장) 대비 사전 등록. 전부 active=False — 법 조문 미검증 상태로
    # 실제 콘텐츠를 만들면 안 되기 때문에, 착수 시점에 검증부터 하고 active=True로 바꾼다.
    "medical_general": {
        "match_keywords": ["병원", "한의원", "피부과", "성형외과", "내과", "정형외과"],
        "banned_terms": ["100% 완치", "무통증 시술", "안전성 보장", "타 병원보다 우수", "환자 치료 후기"],
        "performance_pricing_allowed": False,
        "default_customer_stage": "decision",
        "compliance_note": "의료법 의료광고 규제 — 조문 미검증. 착수 전 검증 필수",
        "active": False,
        "default_freedom_level": 0,
    },
    "beauty": {
        "match_keywords": ["미용실", "헤어샵", "네일샵", "피부관리실"],
        "banned_terms": [],
        "performance_pricing_allowed": True,
        "default_customer_stage": "comparison",
        "compliance_note": "특이 규제 없음 — 표시광고법 기본만 확인",
        "active": False,
        "default_freedom_level": 2,
    },
    "academy": {
        "match_keywords": ["학원", "과외", "교습소"],
        "banned_terms": ["100% 합격", "성적 보장"],
        "performance_pricing_allowed": True,
        "default_customer_stage": "comparison",
        "compliance_note": "학원법상 허위·과장 광고 제한 — 조문 미검증. 착수 전 검증 필수",
        "active": False,
        "default_freedom_level": 1,
    },
    "legal_tax": {
        "match_keywords": ["변호사", "법무법인", "세무사", "회계법인"],
        "banned_terms": ["고객 연결해드립니다", "상담하시면 소개", "성사 시 정산", "승소 보장"],
        "performance_pricing_allowed": False,
        "default_customer_stage": "awareness",
        "compliance_note": "변호사법·세무사법상 사건 소개·알선 제한 소지 — 노무법인과 유사한 구조로 추정되나 조문 미검증. 착수 전 검증 필수",
        "active": False,
        "default_freedom_level": 1,
    },
}


def classify_business(category: str) -> str:
    """카테고리 문자열을 보고 버티컬 키를 반환한다. 매칭 안 되면 'generic'."""

    for vertical, profile in VERTICAL_PROFILES.items():
        if any(kw in category for kw in profile["match_keywords"]):
            return vertical
    return "generic"


def build_business_dna(
    business_name: str,
    category: str,
    explicit_banned_terms: list[str] | None = None,
    explicit_freedom_level: int | None = None,
) -> dict:
    """업종 기본값을 채운 DNA를 반환한다.

    explicit_banned_terms는 프로필 기본값에 병합된다.
    explicit_freedom_level(0~5, 4절 참고)이 주어지면 업종 기본값 대신 그 값을 쓴다 —
    사장님이 특정 업체만 더 보수적으로/자유롭게 설정하고 싶을 때 override용.
    vertical_active가 False인 업종은 freedom_level을 무조건 0으로 강제한다 —
    콘텐츠 생성 자체가 코드 레벨로 막혀있는데 freedom_level만 높게 잡아두면 모순이라서.
    """

    vertical = classify_business(category)
    profile = VERTICAL_PROFILES.get(vertical, {})
    vertical_active = profile.get("active", True)

    banned = list(profile.get("banned_terms", []))
    for term in explicit_banned_terms or []:
        if term not in banned:
            banned.append(term)

    if explicit_freedom_level is not None and explicit_freedom_level not in FREEDOM_LEVELS:
        raise ValueError(f"freedom_level은 0~5여야 합니다 (받은 값: {explicit_freedom_level})")

    if not vertical_active:
        freedom_level = 0
    elif explicit_freedom_level is not None:
        freedom_level = explicit_freedom_level
    else:
        freedom_level = profile.get("default_freedom_level", 1)

    return {
        "business_name": business_name,
        "vertical": vertical,
        "vertical_active": vertical_active,
        "banned_terms": banned,
        "performance_pricing_allowed": profile.get("performance_pricing_allowed", True),
        "default_customer_stage": profile.get("default_customer_stage", "awareness"),
        "compliance_note": profile.get("compliance_note", "일반 업종 — 특이 규제 없음, 그래도 표시광고법 기본은 확인"),
        "freedom_level": freedom_level,
        "freedom_level_label": FREEDOM_LEVELS[freedom_level],
    }


def main():
    for name, category in [("예시식당", "고깃집"), ("예시노무법인", "노무법인"), ("예시치과", "치과"), ("예시학원", "입시학원")]:
        dna = build_business_dna(name, category)
        print(f"{name} ({category}) -> {dna}")


if __name__ == "__main__":
    main()
