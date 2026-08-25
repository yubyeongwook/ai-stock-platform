"""LLM(클로드) 연결 — blog_content_agent가 만든 뼈대(제목/목차/CTA)를 실제 본문으로 채운다.

blog_content_agent.build_blog_draft()는 규칙 기반 뼈대만 만든다(제목 후보, 목차, CTA).
이 모듈이 그 뼈대를 받아 실제 SEO 블로그 본문 문장을 생성한다.

사전 준비물: ANTHROPIC_API_KEY (.env.example 참고)
의존성: pip install anthropic (requirements.txt에 포함)
"""

import os


class LLMWriterConfigError(RuntimeError):
    pass


def _load_client():
    try:
        import anthropic
    except ImportError as e:
        raise LLMWriterConfigError("anthropic 패키지가 설치되어 있지 않습니다. `pip install anthropic`") from e

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMWriterConfigError("ANTHROPIC_API_KEY가 설정되지 않았습니다. .env에 채워 넣으세요.")

    return anthropic.Anthropic(api_key=api_key)


def _build_prompt(draft: dict, business_name: str, category: str, location: str | None, banned_terms: list[str]) -> str:
    banned_line = (
        f"다음 표현은 절대 쓰지 마라(광고 규제 위반 소지): {', '.join(banned_terms)}\n" if banned_terms else ""
    )

    outline_text = "\n".join(draft["outline"])

    return f"""아래 뼈대를 바탕으로 {location or ''} {category} 업체 "{business_name}"를 위한
SEO 블로그 포스트 본문을 한국어로 작성해라.

제목: {draft["title_candidates"][0]}

목차:
{outline_text}

타겟 키워드: {", ".join(draft["keywords"])}

요구사항:
- 목차의 각 항목을 소제목(##)으로 삼아 2~4문단씩 채운다
- 정보 전달 위주로 쓰고, 과장·단정적 효과 표현은 피한다
- 타겟 키워드를 자연스럽게 본문에 녹인다(키워드 스터핑 금지)
- 마지막에 CTA 문장으로 마무리: "{draft["cta"]}"
{banned_line}
마크다운 형식으로 본문만 출력해라 (제목 줄은 이미 있으니 반복하지 마라).
"""


def write_full_blog_post(
    draft: dict,
    business_name: str,
    category: str,
    location: str | None = None,
    banned_terms: list[str] | None = None,
    model: str = "claude-sonnet-5",
) -> str:
    """뼈대(draft)를 받아 실제 블로그 본문 텍스트를 생성해 반환한다."""

    client = _load_client()
    prompt = _build_prompt(draft, business_name, category, location, banned_terms or [])

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    return "".join(block.text for block in response.content if block.type == "text")
