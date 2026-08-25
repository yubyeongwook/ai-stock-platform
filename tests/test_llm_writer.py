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
    prompt = _build_prompt(draft, "예시노무법인", "노무법인", "강남", ["금지표현"])
    assert "금지표현" in prompt


def test_prompt_omits_banned_line_when_empty(draft):
    prompt = _build_prompt(draft, "예시노무법인", "노무법인", "강남", [])
    assert "절대 쓰지 마라" not in prompt


def test_prompt_embeds_playbook_sections(draft):
    prompt = _build_prompt(draft, "예시노무법인", "노무법인", "강남", [])
    assert "네이버 SEO" in prompt
    assert "전환 심리학" in prompt
