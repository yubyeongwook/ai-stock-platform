import pytest

from integrations.kakao_alimtalk import AlimtalkConfigError, KakaoAlimtalkClient


def test_missing_config_raises(monkeypatch):
    monkeypatch.delenv("ALIMTALK_API_BASE_URL", raising=False)
    monkeypatch.delenv("ALIMTALK_API_KEY", raising=False)
    with pytest.raises(AlimtalkConfigError):
        KakaoAlimtalkClient()


def test_dry_run_returns_payload_without_network_call(monkeypatch):
    monkeypatch.setenv("ALIMTALK_API_BASE_URL", "https://example.test/send")
    monkeypatch.setenv("ALIMTALK_API_KEY", "test-key")
    client = KakaoAlimtalkClient()
    result = client.send("010-0000-0000", "REVIEW_REQUEST", {"business_name": "업체"}, dry_run=True)
    assert result["dry_run"] is True
    assert result["payload"]["receiver"] == "010-0000-0000"
    assert result["payload"]["apikey"] == "test-key"
