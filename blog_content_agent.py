"""업종 무관 SEO 블로그 콘텐츠 초안 생성 에이전트.

고객사(업종, 상호명, 타겟 키워드)를 입력받아 블로그 포스트 초안의
구조(제목 후보, 목차, 본문 뼈대, CTA)를 생성한다.
LLM 없이 규칙 기반 템플릿으로 동작해 별도 API 키 없이 바로 실행 가능하다.
실제 서비스에서는 이 뼈대를 LLM에 넘겨 본문을 완성시키는 식으로 확장한다.
"""


def build_blog_draft(business_name: str, category: str, keywords: list[str], location: str | None = None) -> dict:
    if not keywords:
        raise ValueError("keywords는 최소 1개 이상이어야 합니다.")

    primary_keyword = keywords[0]
    location_prefix = f"{location} " if location else ""

    title_candidates = [
        f"{location_prefix}{category} {primary_keyword} 완벽 가이드 | {business_name}",
        f"{primary_keyword}, {business_name}에서 확인하세요",
        f"{location_prefix}{category} 찾으신다면 - {primary_keyword} 총정리",
    ]

    outline = [
        f"1. {primary_keyword}란 무엇인가",
        f"2. {location_prefix}{category} 선택 시 확인해야 할 포인트",
        f"3. {business_name}이(가) 제공하는 차별점",
        "4. 자주 묻는 질문(FAQ)",
        "5. 방문/상담 안내",
    ]

    cta = f"지금 {business_name}에 문의하고 {primary_keyword} 관련 상담을 받아보세요."

    return {
        "title_candidates": title_candidates,
        "outline": outline,
        "keywords": keywords,
        "cta": cta,
    }


def render_markdown(draft: dict) -> str:
    lines = [f"# {draft['title_candidates'][0]}", ""]
    lines.append("## 제목 후보")
    lines += [f"- {t}" for t in draft["title_candidates"]]
    lines.append("")
    lines.append("## 목차")
    lines += [f"- {o}" for o in draft["outline"]]
    lines.append("")
    lines.append(f"## 타겟 키워드: {', '.join(draft['keywords'])}")
    lines.append("")
    lines.append(f"## CTA\n{draft['cta']}")
    return "\n".join(lines)


def main():
    draft = build_blog_draft(
        business_name="예시병원",
        category="정형외과",
        keywords=["무릎 통증 원인", "무릎 통증 병원"],
        location="강남",
    )
    print(render_markdown(draft))


if __name__ == "__main__":
    main()
