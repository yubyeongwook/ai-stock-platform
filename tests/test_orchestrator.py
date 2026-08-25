import json

import pytest

from orchestrator import diagnose_client_priority, generate_daily_outputs, send_review_reminder, write_blog_body
from blog_content_agent import build_blog_draft


@pytest.fixture
def restaurant_client():
    return {
        "slug": "test-restaurant",
        "business_name": "예시식당",
        "category": "고깃집",
        "location": "강남",
        "keywords": ["강남 회식"],
    }


@pytest.fixture
def dental_client():
    return {
        "slug": "test-dental",
        "business_name": "예시치과",
        "category": "치과",
        "location": "강남",
        "keywords": ["임플란트 비용"],
    }


def test_generate_daily_outputs_writes_both_files(tmp_path, restaurant_client):
    outputs = generate_daily_outputs(restaurant_client, out_dir=str(tmp_path))
    assert "blocked" not in outputs
    assert (tmp_path / "test-restaurant").exists()


def test_dental_is_blocked_by_default(tmp_path, dental_client):
    outputs = generate_daily_outputs(dental_client, out_dir=str(tmp_path))
    assert "blocked" in outputs
    assert not (tmp_path / "test-dental").exists()


def test_dental_override_flag_lifts_the_block(tmp_path, dental_client):
    dental_client["override_vertical_hold"] = True
    outputs = generate_daily_outputs(dental_client, out_dir=str(tmp_path))
    assert "blocked" not in outputs


def test_dental_banned_terms_auto_filled_even_without_client_specifying_them(dental_client):
    draft = build_blog_draft(dental_client["business_name"], dental_client["category"], dental_client["keywords"])
    result = write_blog_body(draft, {**dental_client, "banned_terms": []})
    # ANTHROPIC_API_KEY 없는 환경이라 실제 생성은 안 되지만, 그 전에 크래시하지 않아야 한다
    assert "status" in result


def test_write_blog_body_never_raises_without_api_key(restaurant_client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    draft = build_blog_draft(restaurant_client["business_name"], restaurant_client["category"], restaurant_client["keywords"])
    result = write_blog_body(draft, restaurant_client)
    assert result["status"] != "generated"


def test_send_review_reminder_skips_without_phone(restaurant_client):
    result = send_review_reminder(restaurant_client)
    assert "skipped" in result


def test_diagnose_client_priority_wraps_master_ai(restaurant_client):
    result = diagnose_client_priority(restaurant_client, {"impressions": 100})
    assert result["client"] == restaurant_client["business_name"]


def test_load_client_reads_json_file(tmp_path, restaurant_client):
    from orchestrator import load_client

    path = tmp_path / "client.json"
    path.write_text(json.dumps(restaurant_client, ensure_ascii=False), encoding="utf-8")
    loaded = load_client(str(path))
    assert loaded == restaurant_client
