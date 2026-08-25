import pytest

from integrations.ga4_client import GA4ConfigError, get_weekly_summary


def test_missing_property_id_raises_config_error(monkeypatch):
    monkeypatch.delenv("GA4_PROPERTY_ID", raising=False)
    with pytest.raises(GA4ConfigError):
        get_weekly_summary()


def test_missing_package_or_credentials_raises_config_error_not_import_error(monkeypatch):
    """회귀 테스트: property_id는 있지만 패키지 미설치/크리덴셜 미설정일 때
    ModuleNotFoundError가 새어나가면 안 된다 (orchestrator.py가 GA4ConfigError만 잡는다).
    """
    monkeypatch.delenv("GA4_SERVICE_ACCOUNT_JSON", raising=False)
    with pytest.raises(GA4ConfigError):
        get_weekly_summary("123456")
