import pytest

from adsense_readiness_agent import (
    ADSENSE_CERTIFICATION_AUTHORITY_ID,
    audit_adsense_readiness,
    generate_ads_txt,
)


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
