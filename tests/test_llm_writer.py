import pytest

from blog_content_agent import build_blog_draft
from integrations.llm_writer import LLMWriterConfigError, _build_prompt, write_full_blog_post


@pytest.fixture
def draft():
    return build_blog_draft("예시노무법인", "노무법인", ["퇴직금 계산"], "강남")


def test_missing_api_key_raises_clean_error(monkeypatch, draft):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(LLMWriterConfigError):
        write_full_blog_post(draft, "예시노무법인", "노무법인", "강남")


def test_prompt_includes_banned_terms_when_given(draft):
    prompt = _build_prompt(draft, "예시노무법인", "노무법인", "강남", ["금지표현"], [])
    assert "금지표현" in prompt


def test_prompt_omits_banned_line_when_empty(draft):
    prompt = _build_prompt(draft, "예시노무법인", "노무법인", "강남", [], [])
    assert "절대 쓰지 마라" not in prompt


def test_prompt_embeds_playbook_sections(draft):
    prompt = _build_prompt(draft, "예시노무법인", "노무법인", "강남", [], [])
    assert "네이버 SEO" in prompt
    assert "전환 심리학" in prompt


def test_prompt_always_forbids_inventing_operational_facts(draft):
    # 회귀 테스트: 서초김치찌개 파일럿에서 실제로 LLM이 "묵은지 자체 숙성",
    # "매일 국물 우려냄" 같은 확인 안 된 사실을 지어낸 사고가 있었다.
    prompt = _build_prompt(draft, "예시노무법인", "노무법인", "강남", [], [])
    assert "사실 지어내기 금지" in prompt


def test_prompt_includes_known_facts_when_given(draft):
    prompt = _build_prompt(draft, "예시노무법인", "노무법인", "강남", [], ["평일 9시~18시 운영"])
    assert "평일 9시~18시 운영" in prompt
    assert "아래는 실제로 확인된 사실이다" in prompt


def test_prompt_omits_facts_block_when_no_known_facts(draft):
    prompt = _build_prompt(draft, "예시노무법인", "노무법인", "강남", [], [])
    assert "아래는 실제로 확인된 사실이다" not in prompt
