import pytest

from integrations.meta_ads import MetaAdsClient, MetaAdsConfigError


def test_missing_config_raises(monkeypatch):
    monkeypatch.delenv("META_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("META_AD_ACCOUNT_ID", raising=False)
    with pytest.raises(MetaAdsConfigError):
        MetaAdsClient()


def test_dry_run_custom_audience_no_network_call(monkeypatch):
    monkeypatch.setenv("META_ACCESS_TOKEN", "test-token")
    monkeypatch.setenv("META_AD_ACCOUNT_ID", "123")
    client = MetaAdsClient()
    result = client.create_website_custom_audience("리타겟팅 오디언스", dry_run=True)
    assert result["dry_run"] is True
    assert "act_123" in result["endpoint"]
