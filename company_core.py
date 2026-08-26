"""company_core.py — AI GROWTH OS Phase 1: TENANT / COMPANY CORE.

`docs/ai-growth-os-architecture.md` 0단계. 업체 하나(clients/*.json)를 받아
Company ID / Business Profile / Business DNA / Marketing Profile /
Customer Profile / Growth Profile 여섯 묶음으로 정리한다 — 이후 모든 Phase가
같은 업체 데이터를 이 형태로 공유한다.

정직하게 말하면: 이건 "AI가 업체를 분석"하는 게 아니라, clients/*.json에 이미
있는 값을 정해진 6개 카테고리로 재배열하고(business_dna.py 재사용), 사람이
아직 안 채운 필드는 지어내지 않고 None으로 남기는 정리 작업이다. 시장조사·경쟁사
분석처럼 실제 판단이 필요한 건 Phase 4(Business/Customer Intelligence)의 몫이고,
여기서는 안 다룬다.
"""

from business_dna import build_business_dna
from revenue_engine import decompose_goal, estimate_profit_impact


def build_company_profile(client: dict) -> dict:
    """client 딕셔너리(clients/*.json 로드 결과) 하나를 6개 카테고리로 정리한다.

    기존 clients/*.json 스키마와 100% 하위호환된다 — 아래 새 필드들은 전부
    client.get(...)로 조회해서, 없는 파일은 그냥 None/빈 값으로 채워진다.
    기존 온보딩 브리프를 새로 다 채워 넣어야 동작하는 게 아니다.
    """

    dna = build_business_dna(
        client["business_name"],
        client["category"],
        client.get("banned_terms"),
        client.get("freedom_level"),
    )

    business_profile = {
        "business_name": client["business_name"],
        "category": client["category"],
        "location": client.get("location"),
        "homepage": client.get("homepage"),
        "business_description": client.get("business_description"),
        "flagship_product": client.get("flagship_product"),
        "price": client.get("price"),
        "hours": client.get("hours"),
        "employee_count": client.get("employee_count"),
    }

    marketing_profile = {
        "keywords": client.get("keywords", []),
        "existing_channels": client.get("existing_channels", []),
        "ad_budget": client.get("ad_budget"),
        "review_target_phone": client.get("review_target_phone"),
        "ga4_property_id": client.get("ga4_property_id"),
    }

    customer_profile = {
        "existing_customers_summary": client.get("existing_customers_summary"),
        "customer_stage": client.get("customer_stage", dna["default_customer_stage"]),
    }

    revenue = client.get("revenue")
    target_revenue = client.get("target_revenue")
    revenue_gap = (
        target_revenue - revenue if isinstance(revenue, (int, float)) and isinstance(target_revenue, (int, float)) else None
    )
    growth_profile = {
        "revenue": revenue,
        "target_revenue": target_revenue,
        "revenue_gap": revenue_gap,
        "goal_decomposition": (
            decompose_goal(dna["vertical"], revenue_gap, client.get("funnel_rates", {}))
            if revenue_gap is not None
            else None
        ),
        "profit_impact": (
            estimate_profit_impact(revenue_gap, client.get("variable_cost_rate")) if revenue_gap is not None else None
        ),
    }

    return {
        "company_id": client["slug"],
        "business_profile": business_profile,
        "business_dna": dna,
        "marketing_profile": marketing_profile,
        "customer_profile": customer_profile,
        "growth_profile": growth_profile,
    }


def render_summary(profile: dict) -> str:
    """Command Center에서 사람이 훑어볼 요약 — 한 업체를 한 화면에."""

    bp = profile["business_profile"]
    dna = profile["business_dna"]
    gp = profile["growth_profile"]

    lines = [
        f"# {bp['business_name']} ({profile['company_id']})",
        "",
        f"- 업종: {bp['category']} → {dna['vertical']} ({'활성' if dna['vertical_active'] else '보류'})",
        f"- 위치: {bp['location'] or '미입력'}",
        f"- 컴플라이언스: {dna['compliance_note']}",
    ]
    if gp["revenue"] is not None or gp["target_revenue"] is not None:
        lines.append(f"- 매출: {gp['revenue'] or '미입력'} / 목표: {gp['target_revenue'] or '미입력'}")
    return "\n".join(lines)


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Company Core — 업체 프로필 조회")
    parser.add_argument("client_json", help="clients/example-restaurant.json 같은 브리프 파일 경로")
    args = parser.parse_args()

    with open(args.client_json, encoding="utf-8") as f:
        client = json.load(f)

    profile = build_company_profile(client)
    print(render_summary(profile))
    print()
    print(json.dumps(profile, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
