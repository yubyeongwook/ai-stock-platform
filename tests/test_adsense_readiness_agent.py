from unittest.mock import Mock, patch

import pytest
import requests

from adsense_readiness_agent import (
    ADSENSE_CERTIFICATION_AUTHORITY_ID,
    audit_adsense_readiness,
    check_ads_txt,
    check_essential_pages,
    check_https,
    check_robots_txt,
    check_sitemap,
    generate_ads_txt,
    run_full_diagnostic,
)


def _mock_response(status_code=200, text="", content=None):
    resp = Mock()
    resp.status_code = status_code
    resp.text = text
    resp.content = content if content is not None else text.encode("utf-8")
    return resp


# ── 기존 매뉴얼 체크리스트 ──────────────────────────────────────────

def test_audit_counts_ready_and_not_ready_correctly():
    result = audit_adsense_readiness({
        "post_count_and_length_ok": True,
        "essential_pages_present": False,
    })
    assert result["ready_count"] == 1
    assert result["not_ready_count"] == 1
    assert result["unknown_count"] == result["total"] - 2


def test_audit_never_promises_approval():
    result = audit_adsense_readiness({})
    assert "보장할 수 없다" in result["note"]


def test_generate_ads_txt_uses_correct_certification_authority_id():
    line = generate_ads_txt("pub-1234567890123456")
    assert ADSENSE_CERTIFICATION_AUTHORITY_ID in line
    assert line == "google.com, pub-1234567890123456, DIRECT, f08c47fec0942fa0"


def test_generate_ads_txt_rejects_missing_pub_prefix():
    with pytest.raises(ValueError):
        generate_ads_txt("1234567890123456")


# ── 실제 HTTP 진단 함수 (requests.get 모킹) ─────────────────────────

@patch("adsense_readiness_agent.requests.get")
def test_check_https_passes_on_200(mock_get):
    mock_get.return_value = _mock_response(200)
    result = check_https("example.com")
    assert result["passed"] is True


@patch("adsense_readiness_agent.requests.get")
def test_check_https_fails_on_network_error(mock_get):
    mock_get.side_effect = requests.RequestException("connection refused")
    result = check_https("example.com")
    assert result["passed"] is False


@patch("adsense_readiness_agent.requests.get")
def test_check_ads_txt_passes_with_correct_format(mock_get):
    mock_get.return_value = _mock_response(200, text="google.com, pub-1909539956838332, DIRECT, f08c47fec0942fa0")
    result = check_ads_txt("laborcheckai.co.kr", expected_publisher_id="pub-1909539956838332")
    assert result["passed"] is True


@patch("adsense_readiness_agent.requests.get")
def test_check_ads_txt_catches_wrong_certification_authority_id(mock_get):
    # 실제로 발생했던 사고 재현: 인증기관ID 오타
    mock_get.return_value = _mock_response(200, text="google.com, pub-1909539956838332, DIRECT, f00c287a34f70400")
    result = check_ads_txt("laborcheckai.co.kr")
    assert result["passed"] is False
    assert "인증기관ID" in result["detail"]


@patch("adsense_readiness_agent.requests.get")
def test_check_ads_txt_missing_file_fails(mock_get):
    mock_get.return_value = _mock_response(404)
    result = check_ads_txt("example.com")
    assert result["passed"] is False


@patch("adsense_readiness_agent.requests.get")
def test_check_robots_txt_passes_when_crawlers_allowed(mock_get):
    mock_get.return_value = _mock_response(200, text="User-agent: *\nAllow: /\n\nUser-agent: Mediapartners-Google\nAllow: /\n")
    result = check_robots_txt("example.com")
    assert result["passed"] is True


@patch("adsense_readiness_agent.requests.get")
def test_check_robots_txt_fails_when_mediapartners_blocked(mock_get):
    mock_get.return_value = _mock_response(200, text="User-agent: Mediapartners-Google\nDisallow: /\n")
    result = check_robots_txt("example.com")
    assert result["passed"] is False
    assert "Mediapartners-Google" in result["detail"]


@patch("adsense_readiness_agent.requests.get")
def test_check_sitemap_counts_urls(mock_get):
    xml = b"""<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://example.com/a</loc></url>
<url><loc>https://example.com/b</loc></url>
</urlset>"""
    mock_get.return_value = _mock_response(200, content=xml)
    result = check_sitemap("example.com", min_urls=1)
    assert result["url_count"] == 2
    assert result["passed"] is True


@patch("adsense_readiness_agent.requests.get")
def test_check_sitemap_fails_below_threshold(mock_get):
    xml = b'<?xml version="1.0"?><urlset><url><loc>https://example.com/a</loc></url></urlset>'
    mock_get.return_value = _mock_response(200, content=xml)
    result = check_sitemap("example.com", min_urls=15)
    assert result["passed"] is False


@patch("adsense_readiness_agent.requests.get")
def test_check_essential_pages_detects_missing_about(mock_get):
    mock_get.return_value = _mock_response(200, text="<html>개인정보처리방침 문의 링크</html>")
    result = check_essential_pages("example.com")
    assert result["passed"] is False
    assert "about" in result["detail"]


@patch("adsense_readiness_agent.requests.get")
def test_check_essential_pages_all_found(mock_get):
    mock_get.return_value = _mock_response(200, text="<html>소개 개인정보처리방침 문의</html>")
    result = check_essential_pages("example.com")
    assert result["passed"] is True


@patch("adsense_readiness_agent.requests.get")
def test_run_full_diagnostic_never_promises_approval(mock_get):
    mock_get.return_value = _mock_response(200, text="google.com, pub-123, DIRECT, f08c47fec0942fa0")
    result = run_full_diagnostic("example.com", publisher_id="pub-123")
    assert "domain" in result
    assert "보장할 수 없다" in result["note"]
    assert len(result["manual_review_needed"]) > 0
