"""adsense_essential_pages.py — 애드센스 필수 페이지(소개/개인정보처리방침/연락처) 생성.

정직하게 말하면: 아래 개인정보처리방침은 **일반적인 틀**이지, 실제 수집하는 개인정보
항목(쿠키, 로그, 결제정보 등)이 다르면 그대로 쓰면 안 된다 — `docs/service-agreement-template.md`,
`docs/quote-template.md`와 같은 이유로 **실제 발행 전 사장님/고객사가 실제 운영 방식에
맞게 검토·수정**해야 한다. 특히 광고(애드센스)·분석도구(GA4)를 쓰면 관련 고지 문구는
법적으로 사실과 일치해야 한다.
"""


def build_about_page(business_name: str, category: str, known_facts: list[str] | None = None) -> str:
    """known_facts에 있는 것만 구체적으로 쓴다 — 없으면 일반적인 소개문으로만 채운다
    (llm_writer.py와 같은 원칙: 확인 안 된 사실을 지어내지 않는다)."""

    facts_html = ""
    if known_facts:
        items = "\n".join(f"<li>{fact}</li>" for fact in known_facts)
        facts_html = f"<ul>{items}</ul>"

    return f"""<h1>{business_name} 소개</h1>
<p>{business_name}는 {category} 분야에서 운영되고 있습니다.</p>
{facts_html}
<p>문의사항은 연락처 페이지를 통해 남겨주시면 확인 후 답변드리겠습니다.</p>
"""


def build_privacy_policy_page(business_name: str, contact_email: str, uses_ga4: bool = False, uses_adsense: bool = False) -> str:
    """uses_ga4/uses_adsense는 실제로 그 도구를 쓸 때만 True로 넘겨라 — 안 쓰는데 쓴다고
    고지하면 그것도 사실과 다른 문구가 된다."""

    analytics_clause = (
        "<p>본 사이트는 Google Analytics(GA4)를 이용해 방문 통계를 익명으로 수집할 수 있습니다.</p>"
        if uses_ga4 else ""
    )
    adsense_clause = (
        "<p>본 사이트는 Google AdSense를 통해 광고를 게재하며, Google 및 제휴사는 쿠키를 "
        "이용해 사용자의 관심사에 기반한 광고를 표시할 수 있습니다. 광고 개인화를 원치 않으시면 "
        "<a href=\"https://adssettings.google.com\">Google 광고 설정</a>에서 조정할 수 있습니다.</p>"
        if uses_adsense else ""
    )

    return f"""<h1>개인정보처리방침</h1>
<p>{business_name}(이하 "본 사이트")는 이용자의 개인정보를 소중히 다룹니다.</p>
{analytics_clause}
{adsense_clause}
<p>수집한 정보는 서비스 운영 목적 외에 사용하지 않으며, 관련 법령에 따라 안전하게 관리합니다.</p>
<p>본 방침에 대한 문의: {contact_email}</p>
<p><small>※ 이 문서는 일반적인 틀입니다. 실제 수집 항목·처리 방식에 맞게 검토 후 게시하세요.</small></p>
"""


def build_contact_page(business_name: str, contact_email: str, contact_phone: str | None = None) -> str:
    phone_line = f"<p>전화: {contact_phone}</p>" if contact_phone else ""
    return f"""<h1>연락처</h1>
<p>{business_name}에 문의하실 사항은 아래로 연락 주세요.</p>
<p>이메일: {contact_email}</p>
{phone_line}
"""
