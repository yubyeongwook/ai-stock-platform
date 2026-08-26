"""adsense_readiness_agent.py — 애드센스 승인 준비·점검·최적화 에이전트.

정직하게 말하면: **"자동 승인"은 존재하지 않는다.** 애드센스 심사는 구글이 사람 +
자동 시스템으로 직접 하는 것이라, 외부에서 승인 자체를 대신 눌러줄 방법이 없다.
구글도 정확한 통과 기준(글 개수, 글자 수 등 숫자 커트라인)을 공식적으로 공개하지
않는다 — 아래 체크리스트는 구글 공식 정책(support.google.com/adsense/answer/48182,
answer/9724)과 실제 승인 사례들의 공통 패턴을 종합한 것이지, 구글이 보증한 숫자가
아니다. "몇 개 쓰면 100% 붙는다"는 식으로 팔면 안 된다.

이 에이전트가 실제로 파는 것: **승인 확률을 최대화하는 준비·점검·최적화 — 승인
자체는 아님.** 그래서 상품명도 "애드센스 승인 대행"이 아니라 "애드센스 승인 준비
점검"으로 팔아야 한다 (검색순위 1위 보장과 같은 이유로 승인 보장 문구는 금지).

## 출처
- https://support.google.com/adsense/answer/48182 (AdSense Program policies)
- https://support.google.com/adsense/answer/9724 (Eligibility requirements)
- 실제 확인된 ads.txt 인증기관 ID(f08c47fec0942fa0)는 laborcheck-ai 저장소에서
  실제로 오타로 승인/수익에 문제가 됐던 걸 고친 이력으로 재확인됨
"""

ADSENSE_CERTIFICATION_AUTHORITY_ID = "f08c47fec0942fa0"

ADSENSE_CHECKLIST = [
    {
        "category": "콘텐츠 양·질",
        "requirement": "독창적인 글 15~25편 이상, 편당 800~1,000자 이상",
        "why": "글 개수보다 편당 깊이가 더 중요 — 구글의 Helpful Content 기준에서 '검색엔진용'으로 보이는 얕은 글은 감점",
        "field": "post_count_and_length_ok",
    },
    {
        "category": "필수 페이지",
        "requirement": "소개(About), 개인정보처리방침(Privacy Policy), 연락처(Contact) 3종",
        "why": "사이트 신뢰도·운영 주체 확인용 — 없으면 거의 확실하게 반려",
        "field": "essential_pages_present",
    },
    {
        "category": "사이트 운영 기간",
        "requirement": "최소 1개월, 이상적으로는 3~6개월 이상 꾸준히 운영",
        "why": "트래픽이 없어도 통과한 사례는 있으나, 새로 만든 티가 나는 사이트는 불리",
        "field": "site_age_days",
    },
    {
        "category": "기술 요건 — HTTPS",
        "requirement": "커스텀 도메인 + HTTPS 적용",
        "why": "블로그스팟 서브도메인 자체는 문제 없지만, 커스텀 도메인이면 HTTPS는 필수",
        "field": "https_enabled",
    },
    {
        "category": "기술 요건 — ads.txt",
        "requirement": f"루트에 `google.com, pub-<발행자ID>, DIRECT, {ADSENSE_CERTIFICATION_AUTHORITY_ID}` 형식으로 정확히 배치",
        "why": "인증기관 ID 오타 하나로 '비인증 판매자'로 분류돼 광고·수익에 문제가 생긴 실제 사례 있음",
        "field": "ads_txt_correct",
    },
    {
        "category": "기술 요건 — robots.txt",
        "requirement": "Googlebot과 Mediapartners-Google(애드센스 광고 매칭용 크롤러)을 명시적으로 허용",
        "why": "Mediapartners-Google이 막혀있으면 애드센스가 페이지 내용을 못 읽어 광고 매칭·심사에 불리",
        "field": "robots_txt_allows_adsense_crawlers",
    },
    {
        "category": "정책 준수",
        "requirement": "성인·폭력·저작권 침해 등 금지 콘텐츠 없음, 자동생성 콘텐츠도 편집 검수 흔적 필요",
        "why": "AI 생성 콘텐츠 자체가 금지는 아니지만, 편집 없이 그대로 발행된 티가 나면 불리(Helpful Content 정책)",
        "field": "no_prohibited_content",
    },
    {
        "category": "모바일 최적화",
        "requirement": "모바일에서 레이아웃 깨짐 없이 정상 표시",
        "why": "구글 심사·크롤링 자체가 모바일 우선(mobile-first)",
        "field": "mobile_friendly",
    },
]


## ────────────────────────────────────────────────────────────────
## 실제 HTTP 진단 — 이 저장소가 실행되는 환경(예: 이 저장소 자체 GitHub Actions,
## 또는 aigoid-blog-bot·laborcheck-ai의 GitHub Actions)처럼 실제 인터넷 접근이
## 되는 곳에서 실행하면, 매뉴얼로 True/False를 채워 넣을 필요 없이 실제 사이트를
## 직접 확인한다. (참고: 이 매출엔진 세션 자체는 보안 정책상 임의 외부 도메인으로
## 직접 HTTP 요청을 못 하게 막혀 있어 여기서는 라이브 테스트를 못 했다 — 로직은
## requests 라이브러리의 정상적인 사용법이고, 단위 테스트는 응답을 모킹해서 검증함.)
## ────────────────────────────────────────────────────────────────

import re as _re
import xml.etree.ElementTree as _ET

import requests

REQUEST_TIMEOUT = 10
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AdSenseReadinessChecker/1.0)"}


def _safe_get(url: str):
    """requests.get을 감싸서 (성공여부, 응답객체 또는 에러문자열) 튜플로 반환한다.
    네트워크 오류를 조용히 삼키지 않는다 — 호출부가 반드시 확인해야 한다."""
    try:
        return True, requests.get(url, timeout=REQUEST_TIMEOUT, headers=_HEADERS)
    except requests.RequestException as e:
        return False, str(e)


def check_https(domain: str) -> dict:
    ok, resp = _safe_get(f"https://{domain}")
    if not ok:
        return {"passed": False, "detail": f"HTTPS 접속 실패: {resp}"}
    return {"passed": resp.status_code < 400, "detail": f"HTTP {resp.status_code}"}


def check_ads_txt(domain: str, expected_publisher_id: str | None = None) -> dict:
    """expected_publisher_id 예: 'pub-1909539956838332'. 안 넘기면 인증기관ID만 확인한다."""

    ok, resp = _safe_get(f"https://{domain}/ads.txt")
    if not ok:
        return {"passed": None, "detail": f"조회 실패(네트워크 오류): {resp}"}
    if resp.status_code == 404:
        return {"passed": False, "detail": "ads.txt 파일이 존재하지 않음"}
    if resp.status_code >= 400:
        return {"passed": None, "detail": f"확인 불가 (HTTP {resp.status_code})"}

    text = resp.text
    problems = []
    if "google.com" not in text:
        problems.append("google.com 판매자 항목이 없음")
    if ADSENSE_CERTIFICATION_AUTHORITY_ID not in text:
        problems.append(f"인증기관ID({ADSENSE_CERTIFICATION_AUTHORITY_ID})가 없음 — 오타 가능성 있음")
    if expected_publisher_id and expected_publisher_id not in text:
        problems.append(f"지정한 퍼블리셔ID({expected_publisher_id})가 파일에 없음")

    return {
        "passed": not problems,
        "detail": "; ".join(problems) if problems else "정상",
        "raw": text[:500],
    }


def check_robots_txt(domain: str) -> dict:
    """Googlebot·Mediapartners-Google(애드센스 크롤러)이 차단돼 있지 않은지 확인한다."""

    ok, resp = _safe_get(f"https://{domain}/robots.txt")
    if not ok:
        return {"passed": None, "detail": f"조회 실패(네트워크 오류): {resp}"}
    if resp.status_code >= 400:
        # robots.txt가 아예 없으면 관례상 "전부 허용"으로 취급되지만, 확신할 수 없어 unknown 처리
        return {"passed": None, "detail": f"robots.txt 없음/접근 불가 (HTTP {resp.status_code})"}

    text = resp.text
    blocked_agents = []
    for agent in ["Mediapartners-Google", "Googlebot"]:
        block = _re.search(rf"User-agent:\s*{agent}\b(.*?)(?=\nUser-agent:|\Z)", text, _re.IGNORECASE | _re.DOTALL)
        if block and _re.search(r"^\s*Disallow:\s*/\s*$", block.group(1), _re.MULTILINE):
            blocked_agents.append(agent)

    if blocked_agents:
        return {"passed": False, "detail": f"차단된 크롤러: {', '.join(blocked_agents)}"}
    return {"passed": True, "detail": "Googlebot·Mediapartners-Google 차단 없음"}


def check_sitemap(domain: str, min_urls: int = 15) -> dict:
    """sitemap.xml의 URL 개수를 센다 — 콘텐츠 "양"의 대략적 지표(질은 별도 확인 필요)."""

    ok, resp = _safe_get(f"https://{domain}/sitemap.xml")
    if not ok:
        return {"passed": None, "url_count": None, "detail": f"조회 실패(네트워크 오류): {resp}"}
    if resp.status_code >= 400:
        return {"passed": None, "url_count": None, "detail": f"sitemap.xml 없음/접근 불가 (HTTP {resp.status_code})"}

    try:
        root = _ET.fromstring(resp.content)
    except _ET.ParseError:
        return {"passed": None, "url_count": None, "detail": "sitemap.xml 파싱 실패(형식 오류)"}

    count = len([el for el in root.iter() if el.tag.endswith("loc")])
    return {
        "passed": count >= min_urls,
        "url_count": count,
        "detail": f"URL {count}개 발견 (권장 {min_urls}개 이상) — 개수일 뿐 글자 수·품질은 별도 확인 필요",
    }


def check_essential_pages(domain: str) -> dict:
    """홈페이지 HTML에서 소개/개인정보처리방침/연락처로 보이는 링크·문구를 찾는다.
    오탐 가능성이 있는 휴리스틱이다 — "찾음"이 곧 "품질이 충분함"을 뜻하지 않는다,
    실제 페이지 내용은 사람이 확인해야 한다."""

    ok, resp = _safe_get(f"https://{domain}")
    if not ok:
        return {"passed": None, "detail": f"조회 실패(네트워크 오류): {resp}"}
    if resp.status_code >= 400:
        return {"passed": None, "detail": f"홈페이지 접근 불가 (HTTP {resp.status_code})"}

    html = resp.text.lower()
    found = {
        "about": any(kw in html for kw in ["소개", "about"]),
        "privacy": any(kw in html for kw in ["개인정보처리방침", "개인정보", "privacy policy", "privacy"]),
        "contact": any(kw in html for kw in ["연락처", "문의", "contact"]),
    }
    missing = [k for k, v in found.items() if not v]
    return {
        "passed": not missing,
        "found": found,
        "detail": f"홈페이지에서 못 찾음: {', '.join(missing)} (실제 페이지 존재 여부는 링크를 직접 확인)" if missing else "3종 모두 홈페이지에서 링크/문구 확인됨",
    }


def run_full_diagnostic(domain: str, publisher_id: str | None = None) -> dict:
    """도메인 하나를 실제로 진단한다. 실행 환경에 인터넷 접근이 있어야 의미가 있다
    (예: GitHub Actions workflow_dispatch로 실행). 판단 안 되는 항목은 None(확인 불가)로
    남기고, 자동으로 못 보는 항목(콘텐츠 품질·정책 위반 여부·운영 기간)은
    manual_review_needed에 목록으로 남긴다 — 승인 여부는 예측·보장하지 않는다."""

    checks = {
        "https": check_https(domain),
        "ads_txt": check_ads_txt(domain, publisher_id),
        "robots_txt": check_robots_txt(domain),
        "sitemap": check_sitemap(domain),
        "essential_pages": check_essential_pages(domain),
    }

    return {
        "domain": domain,
        "checks": checks,
        "passed_count": sum(1 for c in checks.values() if c.get("passed") is True),
        "failed_count": sum(1 for c in checks.values() if c.get("passed") is False),
        "unknown_count": sum(1 for c in checks.values() if c.get("passed") is None),
        "manual_review_needed": [
            "콘텐츠 양·질(편당 800~1,000자 이상, 15~25편 이상, 독창성) — 자동 판단 불가, 사람이 직접 확인",
            "정책 위반 콘텐츠(성인·폭력·저작권 침해 등) 여부 — 자동 판단 불가",
            "사이트 운영 기간(최소 1개월, 이상적으로 3~6개월) — 도메인 등록일/최초 발행일 별도 확인",
        ],
        "note": "이 진단은 통과 확률을 높이는 준비 상태만 보여준다 — 최종 승인은 구글이 결정하며 보장할 수 없다",
    }


def audit_adsense_readiness(site_info: dict) -> dict:
    """site_info의 각 필드를 체크리스트와 대조해 준비 상태를 점검한다.

    site_info 키는 ADSENSE_CHECKLIST의 "field" 값과 매칭된다. True/False/None(미확인)
    셋 중 하나로 채워서 넘긴다. 승인 여부를 예측하지 않는다 — 무엇이 안 됐는지만 알려준다."""

    results = []
    for item in ADSENSE_CHECKLIST:
        status = site_info.get(item["field"])
        results.append({**item, "status": status})

    ready = [r for r in results if r["status"] is True]
    not_ready = [r for r in results if r["status"] is False]
    unknown = [r for r in results if r["status"] is None]

    return {
        "ready_count": len(ready),
        "not_ready_count": len(not_ready),
        "unknown_count": len(unknown),
        "total": len(results),
        "not_ready_items": [r["requirement"] for r in not_ready],
        "unknown_items": [r["requirement"] for r in unknown],
        "note": "이 점검은 승인 확률을 높이는 준비 상태만 보여준다 — 최종 승인은 구글이 결정하며 보장할 수 없다",
    }


def generate_ads_txt(publisher_id: str) -> str:
    """publisher_id 예: 'pub-1909539956838332' (앞에 'pub-' 포함해서 넘겨라)."""

    if not publisher_id.startswith("pub-"):
        raise ValueError("publisher_id는 'pub-'로 시작해야 한다 (애드센스 계정 설정에서 확인)")

    return f"google.com, {publisher_id}, DIRECT, {ADSENSE_CERTIFICATION_AUTHORITY_ID}"


ADSENSE_ROBOTS_RULES = """User-agent: *
Allow: /

User-agent: Mediapartners-Google
Allow: /

User-agent: Googlebot
Allow: /
"""


def _print_diagnostic_report(result: dict) -> None:
    print(f"\n=== 애드센스 준비 진단: {result['domain']} ===")
    for name, check in result["checks"].items():
        status = check.get("passed")
        mark = "✅" if status is True else "❌" if status is False else "❓"
        print(f"{mark} {name}: {check.get('detail')}")
    print(f"\n통과 {result['passed_count']} / 실패 {result['failed_count']} / 확인불가 {result['unknown_count']}")
    print("\n사람이 직접 확인해야 하는 항목:")
    for item in result["manual_review_needed"]:
        print(f"  - {item}")
    print(f"\n※ {result['note']}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="애드센스 승인 준비 진단")
    parser.add_argument("--domain", help="진단할 도메인 (예: blog.aistoag.com) — 넘기면 실제 HTTP 진단 실행")
    parser.add_argument("--publisher-id", help="애드센스 퍼블리셔 ID (예: pub-1909539956838332)")
    args = parser.parse_args()

    if args.domain:
        result = run_full_diagnostic(args.domain, publisher_id=args.publisher_id)
        _print_diagnostic_report(result)
        return

    # --domain 없이 실행하면 매뉴얼 체크리스트 예시만 보여준다 (데모용)
    example = audit_adsense_readiness({
        "post_count_and_length_ok": True,
        "essential_pages_present": False,
        "site_age_days": 20,
        "https_enabled": True,
        "ads_txt_correct": None,
        "robots_txt_allows_adsense_crawlers": None,
        "no_prohibited_content": True,
        "mobile_friendly": True,
    })
    print(example)
    print(generate_ads_txt("pub-1234567890123456"))
    print("\n실제 사이트를 진단하려면: python3 adsense_readiness_agent.py --domain blog.aistoag.com")


if __name__ == "__main__":
    main()
