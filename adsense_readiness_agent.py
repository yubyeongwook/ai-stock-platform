"""adsense_readiness_agent.py — 애드센스 승인 준비·점검·최적화 에이전트.

정직하게 말하면: **"자동 승인"은 존재하지 않는다.** 애드센스 심사는 구글이 사람 +
자동 시스템으로 직접 하는 것이라, 외부에서 승인 자체를 대신 눌러줄 방법이 없다.
구글도 정확한 통과 기준(글 개수, 글자 수 등 숫자 커트라인)을 공식적으로 공개하지
않는다 — 아래 체크리스트는 구글 공식 정책(support.google.com/adsense/answer/48182,
answer/9724)과 실제 승인 사례들의 공통 패턴을 종합한 것이지, 구글이 보증한 숫자가
아니다. "몇 개 쓰면 100% 붙는다"는 식으로 팔면 안 된다.

이 에이전트가 실제로 파는 것: **승인 확률을 최대화하는 준비·점검·최적화 — 승인
자체는 아님.** 그래서 상품명도 "애드센스 승인 대행"이 아니라 "애드센스 승인 준비
점검"으로 팔아야 한다 (검색순위 1위 보장과 같은 이유로 승인 보장 문구는 금지).

## 출처
- https://support.google.com/adsense/answer/48182 (AdSense Program policies)
- https://support.google.com/adsense/answer/9724 (Eligibility requirements)
- 실제 확인된 ads.txt 인증기관 ID(f08c47fec0942fa0)는 laborcheck-ai 저장소에서
  실제로 오타로 승인/수익에 문제가 됐던 걸 고친 이력으로 재확인됨
"""

ADSENSE_CERTIFICATION_AUTHORITY_ID = "f08c47fec0942fa0"

ADSENSE_CHECKLIST = [
    {
        "category": "콘텐츠 양·질",
        "requirement": "독창적인 글 15~25편 이상, 편당 800~1,000자 이상",
        "why": "글 개수보다 편당 깊이가 더 중요 — 구글의 Helpful Content 기준에서 '검색엔진용'으로 보이는 얕은 글은 감점",
        "field": "post_count_and_length_ok",
    },
    {
        "category": "필수 페이지",
        "requirement": "소개(About), 개인정보처리방침(Privacy Policy), 연락처(Contact) 3종",
        "why": "사이트 신뢰도·운영 주체 확인용 — 없으면 거의 확실하게 반려",
        "field": "essential_pages_present",
    },
    {
        "category": "사이트 운영 기간",
        "requirement": "최소 1개월, 이상적으로는 3~6개월 이상 꾸준히 운영",
        "why": "트래픽이 없어도 통과한 사례는 있으나, 새로 만든 티가 나는 사이트는 불리",
        "field": "site_age_days",
    },
    {
        "category": "기술 요건 — HTTPS",
        "requirement": "커스텀 도메인 + HTTPS 적용",
        "why": "블로그스팟 서브도메인 자체는 문제 없지만, 커스텀 도메인이면 HTTPS는 필수",
        "field": "https_enabled",
    },
    {
        "category": "기술 요건 — ads.txt",
        "requirement": f"루트에 `google.com, pub-<발행자ID>, DIRECT, {ADSENSE_CERTIFICATION_AUTHORITY_ID}` 형식으로 정확히 배치",
        "why": "인증기관 ID 오타 하나로 '비인증 판매자'로 분류돼 광고·수익에 문제가 생긴 실제 사례 있음",
        "field": "ads_txt_correct",
    },
    {
        "category": "기술 요건 — robots.txt",
        "requirement": "Googlebot과 Mediapartners-Google(애드센스 광고 매칭용 크롤러)을 명시적으로 허용",
        "why": "Mediapartners-Google이 막혀있으면 애드센스가 페이지 내용을 못 읽어 광고 매칭·심사에 불리",
        "field": "robots_txt_allows_adsense_crawlers",
    },
    {
        "category": "정책 준수",
        "requirement": "성인·폭력·저작권 침해 등 금지 콘텐츠 없음, 자동생성 콘텐츠도 편집 검수 흔적 필요",
        "why": "AI 생성 콘텐츠 자체가 금지는 아니지만, 편집 없이 그대로 발행된 티가 나면 불리(Helpful Content 정책)",
        "field": "no_prohibited_content",
    },
    {
        "category": "모바일 최적화",
        "requirement": "모바일에서 레이아웃 깨짐 없이 정상 표시",
        "why": "구글 심사·크롤링 자체가 모바일 우선(mobile-first)",
        "field": "mobile_friendly",
    },
]


def audit_adsense_readiness(site_info: dict) -> dict:
    """site_info의 각 필드를 체크리스트와 대조해 준비 상태를 점검한다.

    site_info 키는 ADSENSE_CHECKLIST의 "field" 값과 매칭된다. True/False/None(미확인)
    셋 중 하나로 채워서 넘긴다. 승인 여부를 예측하지 않는다 — 무엇이 안 됐는지만 알려준다."""

    results = []
    for item in ADSENSE_CHECKLIST:
        status = site_info.get(item["field"])
        results.append({**item, "status": status})

    ready = [r for r in results if r["status"] is True]
    not_ready = [r for r in results if r["status"] is False]
    unknown = [r for r in results if r["status"] is None]

    return {
        "ready_count": len(ready),
        "not_ready_count": len(not_ready),
        "unknown_count": len(unknown),
        "total": len(results),
        "not_ready_items": [r["requirement"] for r in not_ready],
        "unknown_items": [r["requirement"] for r in unknown],
        "note": "이 점검은 승인 확률을 높이는 준비 상태만 보여준다 — 최종 승인은 구글이 결정하며 보장할 수 없다",
    }


def generate_ads_txt(publisher_id: str) -> str:
    """publisher_id 예: 'pub-1909539956838332' (앞에 'pub-' 포함해서 넘겨라)."""

    if not publisher_id.startswith("pub-"):
        raise ValueError("publisher_id는 'pub-'로 시작해야 한다 (애드센스 계정 설정에서 확인)")

    return f"google.com, {publisher_id}, DIRECT, {ADSENSE_CERTIFICATION_AUTHORITY_ID}"


ADSENSE_ROBOTS_RULES = """User-agent: *
Allow: /

User-agent: Mediapartners-Google
Allow: /

User-agent: Googlebot
Allow: /
"""


def main():
    example = audit_adsense_readiness({
        "post_count_and_length_ok": True,
        "essential_pages_present": False,
        "site_age_days": 20,
        "https_enabled": True,
        "ads_txt_correct": None,
        "robots_txt_allows_adsense_crawlers": None,
        "no_prohibited_content": True,
        "mobile_friendly": True,
    })
    print(example)
    print(generate_ads_txt("pub-1234567890123456"))


if __name__ == "__main__":
    main()
