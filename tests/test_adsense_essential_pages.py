from adsense_essential_pages import build_about_page, build_contact_page, build_privacy_policy_page


def test_about_page_includes_known_facts_only():
    html = build_about_page("서초김치찌개", "한식 맛집", ["충주사과김치로 김치를 찐다"])
    assert "충주사과김치로 김치를 찐다" in html


def test_about_page_without_known_facts_stays_generic():
    html = build_about_page("서초김치찌개", "한식 맛집", None)
    assert "<ul>" not in html


def test_privacy_policy_omits_adsense_clause_when_not_used():
    html = build_privacy_policy_page("서초김치찌개", "test@example.com", uses_adsense=False)
    assert "AdSense" not in html


def test_privacy_policy_includes_adsense_clause_when_used():
    html = build_privacy_policy_page("서초김치찌개", "test@example.com", uses_adsense=True)
    assert "AdSense" in html
    assert "adssettings.google.com" in html


def test_contact_page_includes_email():
    html = build_contact_page("서초김치찌개", "test@example.com")
    assert "test@example.com" in html
