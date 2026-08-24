"""로컬/플레이스(지도 검색) 마케팅 체크리스트 및 문구 생성 에이전트.

고객사가 '특정한 곳'(매장·병원·업체)으로서 검색·지도에서 먼저 발견되도록
네이버 플레이스 등 로컬 검색 채널 최적화 체크리스트와 리뷰 유도 문구를 생성한다.
"""

CHECKLIST_TEMPLATE = [
    "업체명·카테고리·주소·전화번호(NAP)가 모든 채널에서 100% 일치하는지 확인",
    "대표 이미지·내부 사진 10장 이상 등록, 계절/이벤트별 갱신",
    "영업시간·휴무일 최신 상태 유지",
    "핵심 키워드를 포함한 업체 소개문 작성 (예: '{location} {category} {business_name}')",
    "예약/문의 버튼 등 전환 유도 요소 설정",
    "월 1회 이상 소식(공지) 등록으로 활동성 유지",
]


def build_review_prompt(business_name: str) -> str:
    return (
        f"{business_name}을(를) 이용해 주셔서 감사합니다! "
        "만족스러우셨다면 다른 분들께도 도움이 되도록 짧은 리뷰 부탁드립니다. "
        "불편한 점이 있으셨다면 먼저 말씀해 주세요, 바로 개선하겠습니다."
    )


def build_negative_review_response() -> str:
    return (
        "소중한 의견 감사합니다. 불편을 드려 죄송합니다. "
        "말씀해주신 부분은 확인 후 개선하겠습니다. "
        "자세한 상황을 알려주시면 빠르게 도와드리겠습니다."
    )


def build_local_marketing_plan(business_name: str, category: str, location: str) -> dict:
    checklist = [item.format(location=location, category=category, business_name=business_name) for item in CHECKLIST_TEMPLATE]

    return {
        "checklist": checklist,
        "review_request": build_review_prompt(business_name),
        "negative_review_response": build_negative_review_response(),
    }


def render_markdown(plan: dict, business_name: str, category: str, location: str) -> str:
    lines = [f"# {location} {category} '{business_name}' 로컬 마케팅 플랜", ""]
    lines.append("## 플레이스 최적화 체크리스트")
    lines += [f"- [ ] {item}" for item in plan["checklist"]]
    lines.append("")
    lines.append("## 리뷰 요청 문구")
    lines.append(plan["review_request"])
    lines.append("")
    lines.append("## 부정 리뷰 대응 문구")
    lines.append(plan["negative_review_response"])
    return "\n".join(lines)


def main():
    plan = build_local_marketing_plan(business_name="예시병원", category="정형외과", location="강남")
    print(render_markdown(plan, business_name="예시병원", category="정형외과", location="강남"))


if __name__ == "__main__":
    main()
