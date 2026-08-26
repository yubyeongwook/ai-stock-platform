"""competitor_agent.py — 경쟁분석 에이전트.

정직하게 말하면: 이 에이전트는 경쟁사를 "찾아내지" 않는다. 이 저장소엔 실시간 웹
검색 연동이 없어서, LLM에게 "이 지역 경쟁사가 누구냐"고 물으면 높은 확률로
존재하지 않는 업체를 지어낸다 — `integrations/llm_writer.py`에서 실제로 겪은
환각 사고(서초김치찌개 "묵은지 자체 숙성" 등)와 같은 종류의 위험이다.

그래서 이 에이전트는 **사장님이 실제로 아는 경쟁사 목록(known_competitors)을
입력받아서, 그 정보를 바탕으로 포지셔닝 분석만** 한다. 경쟁사 존재·강점·약점을
LLM이 지어내는 건 이 파일 전체에서 금지한다 — known_competitors가 비어있으면
분석 자체를 하지 않고 그 사실을 그대로 알린다.
"""

import os


class CompetitorAgentConfigError(RuntimeError):
    pass


def _load_client():
    try:
        import anthropic
    except ImportError as e:
        raise CompetitorAgentConfigError("anthropic 패키지가 설치되어 있지 않습니다. `pip install anthropic`") from e

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise CompetitorAgentConfigError("ANTHROPIC_API_KEY가 설정되지 않았습니다. .env에 채워 넣으세요.")

    return anthropic.Anthropic(api_key=api_key)


def build_competitor_brief(business_name: str, category: str, known_competitors: list[dict] | None) -> dict:
    """known_competitors 예:
        [{"name": "OO식당", "strength": "가격이 쌈", "weakness": "주차 불편"}, ...]

    known_competitors가 없으면 분석하지 않고 이유를 그대로 반환한다 — 지어내지 않는다."""

    if not known_competitors:
        return {
            "status": "블로킹: 경쟁사 정보 없음",
            "reason": "known_competitors를 채워야 분석 가능 — 이 에이전트는 경쟁사를 지어내지 않는다",
            "action_needed": "사장님이 실제로 아는 경쟁 업체 이름·강점·약점을 최소 1곳 이상 입력",
        }

    names = [c.get("name", "이름 미상") for c in known_competitors]
    return {
        "status": "분석 가능",
        "business_name": business_name,
        "category": category,
        "competitor_count": len(known_competitors),
        "competitor_names": names,
    }


def _build_prompt(business_name: str, category: str, location: str | None, known_competitors: list[dict]) -> str:
    competitor_lines = "\n".join(
        f"- {c.get('name', '이름 미상')}: 강점({c.get('strength', '미상')}) / 약점({c.get('weakness', '미상')})"
        for c in known_competitors
    )

    return f"""너는 로컬 비즈니스 포지셔닝 전략가다.
아래는 "{location or ''} {category}" 업체 "{business_name}"의 사장님이 직접 파악한
실제 경쟁사 정보다 — 이 목록에 없는 업체는 절대 언급하지 마라, 지어내지 마라.

경쟁사 목록:
{competitor_lines}

**절대 규칙**: 위 목록에 없는 경쟁사 이름·강점·약점을 지어내지 마라. 목록에 없는
정보가 필요하면 "확인 필요"라고만 표시해라.

요구사항:
1. 각 경쟁사 대비 "{business_name}"가 차별화할 수 있는 포지셔닝 각도를 1개씩 제안
2. 위 경쟁사들의 공통 약점(있다면)을 뚫을 수 있는 메시지 방향 1개 제안
3. 전부 위에 주어진 정보에만 근거해서, 조건부·서술형으로("~라면 ~할 여지가 있다")
   쓰고 확언하지 마라

JSON 형식으로만 출력해라:
{{"positioning_angles": ["...", "..."], "shared_weakness_message": "..."}}
"""


def analyze_positioning(
    business_name: str,
    category: str,
    known_competitors: list[dict],
    location: str | None = None,
    model: str = "claude-sonnet-5",
) -> dict:
    """known_competitors 기반으로 포지셔닝 분석을 생성한다. 빈 리스트면 호출하지 마라 —
    build_competitor_brief()로 먼저 확인해라."""

    if not known_competitors:
        raise CompetitorAgentConfigError("known_competitors가 비어있음 — build_competitor_brief()로 먼저 확인해라")

    client = _load_client()
    prompt = _build_prompt(business_name, category, location, known_competitors)

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    return {"raw_text": "".join(block.text for block in response.content if block.type == "text")}


def main():
    example = build_competitor_brief("서초김치찌개", "한식 맛집", [])
    print("빈 목록:", example)

    example2 = build_competitor_brief(
        "서초김치찌개", "한식 맛집",
        [{"name": "옆집 김치찌개", "strength": "가격이 더 쌈", "weakness": "주차 공간 없음"}],
    )
    print("목록 있음:", example2)


if __name__ == "__main__":
    main()
