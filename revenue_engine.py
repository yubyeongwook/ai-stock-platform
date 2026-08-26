"""revenue_engine.py — Revenue Equation Engine + Goal Decomposer.

`docs/ai-growth-os-future-vision.md` 6·7절의 최소 정직한 버전. 업종별 매출 방정식으로
목표매출(또는 매출 격차)을 역산해 "얼마나 더 필요한가"를 계산한다.

이건 학습된 AI 판단이 아니라 **순수 나눗셈**이다 — competitor_agent.py와 같은 원칙을
따른다: 업체가 실제로 측정한 전환율만 쓰고, 모르는 값을 업계 평균으로 대신 채우지
않는다. 업계 평균을 이 업체의 실제 숫자인 것처럼 넣어서 계산하면 "필요 유입
1,840명" 같은 구체적인 숫자가 나오는데, 그 정밀함이 가짜라서 오히려 위험하다.
값이 없으면 "측정 필요"만 알려주고 계산을 멈춘다.
"""

# 업종별 매출 방정식 — 매출 = 마지막 stage부터 역산(나눗셈)해서 앞 단계로 거슬러 올라간다.
# field는 client 브리프/실측 데이터에 있어야 하는 키. 순서는 "매출에 가장 가까운 것"부터.
REVENUE_EQUATIONS = {
    "restaurant": {
        "formula": "매출 = 유입 × 방문전환율 × 객단가 × 방문빈도",
        "steps": [
            {"stage": "거래건수", "field": "avg_order_value", "label": "객단가", "unit": "원/건"},
            {"stage": "방문객수", "field": "visit_conversion_rate", "label": "방문전환율(유입 대비 실제 방문/주문 비율)"},
        ],
    },
    "labor_firm": {
        "formula": "매출 = Lead × 상담전환율 × 계약전환율 × 평균 계약금액",
        "steps": [
            {"stage": "계약건수", "field": "avg_contract_value", "label": "평균 계약금액", "unit": "원/건"},
            {"stage": "상담건수", "field": "contract_conversion_rate", "label": "계약전환율(상담 대비)"},
            {"stage": "Lead수", "field": "consult_conversion_rate", "label": "상담전환율(Lead 대비)"},
        ],
    },
    "dental": {
        "formula": "매출 = 문의 × 예약전환율 × 내원율 × 치료전환율 × 평균 치료금액",
        "steps": [
            {"stage": "치료건수", "field": "avg_treatment_value", "label": "평균 치료금액", "unit": "원/건"},
            {"stage": "내원건수", "field": "treatment_conversion_rate", "label": "치료전환율(내원 대비)"},
            {"stage": "예약건수", "field": "visit_rate", "label": "내원율(예약 대비)"},
            {"stage": "문의건수", "field": "reservation_conversion_rate", "label": "예약전환율(문의 대비)"},
        ],
    },
}


def decompose_goal(vertical: str, revenue_gap: float, known_rates: dict) -> dict:
    """목표매출과의 격차(revenue_gap)를 업종별 방정식으로 역산한다.

    known_rates: {field: value} — 업체가 실제로 측정해서 알려준 값만 넣는다.
    필요한 필드 중 하나라도 없으면 그 지점에서 멈추고 "측정 필요" 목록을 반환한다
    (업계 평균으로 대신 채우지 않음 — competitor_agent.py와 같은 거부 원칙).
    """

    if vertical not in REVENUE_EQUATIONS:
        return {
            "status": "미지원 업종",
            "detail": f"'{vertical}' 업종의 매출 방정식이 아직 정의되지 않았습니다",
        }

    if revenue_gap is None or revenue_gap <= 0:
        return {
            "status": "목표 달성됨" if revenue_gap == 0 else "입력 오류",
            "detail": "revenue_gap이 0이거나 음수입니다 — 이미 목표를 달성했거나 목표매출이 현재보다 낮습니다"
            if revenue_gap is not None
            else "revenue_gap이 없습니다",
        }

    equation = REVENUE_EQUATIONS[vertical]
    missing = [step["label"] for step in equation["steps"] if not known_rates.get(step["field"])]
    if missing:
        return {
            "status": "데이터 부족",
            "formula": equation["formula"],
            "missing_fields": missing,
            "detail": (
                f"{', '.join(missing)}을(를) 실제로 측정해서 알려주셔야 역산할 수 있습니다 — "
                "업계 평균으로 대신 계산하지 않습니다(이 업체의 실제 숫자가 아니라서 오히려 오해를 만듦)"
            ),
        }

    count = revenue_gap
    trace = [{"stage": "필요 추가 매출", "value": round(revenue_gap)}]
    for step in equation["steps"]:
        rate = known_rates[step["field"]]
        count = count / rate
        trace.append({"stage": step["stage"], "value": round(count, 1), "divided_by": f"{step['label']}={rate}"})

    return {
        "status": "계산 완료",
        "formula": equation["formula"],
        "revenue_gap": revenue_gap,
        "trace": trace,
        "required_top_of_funnel": trace[-1]["value"],
        "note": "전부 업체가 실제로 알려준 값 기준 역산 — 업계 평균 추정치 아님",
    }


def what_if(vertical: str, revenue_gap: float, known_rates: dict, delta_pct: float = 0.1) -> dict:
    """어느 지표를 개선하는 게 가장 효율적인 지렛대인지 비교한다 (V5.0 "Counterfactual Engine"의
    정직한 최소 버전 — 순수 산수, 학습된 예측 아님).

    known_rates에 있는 값들 각각을 delta_pct(기본 10%)만큼 올렸다고 가정하고,
    필요 유입(required_top_of_funnel)이 얼마나 줄어드는지 비교해서 랭킹매긴다.
    실행 난이도·비용은 반영 안 한다 — "수학적으로 어느 지렛대가 큰가"만 알려준다,
    "어느 게 쉽다/싸다"는 사람이 판단해야 한다.
    """

    baseline = decompose_goal(vertical, revenue_gap, known_rates)
    if baseline["status"] != "계산 완료":
        return {
            "status": baseline["status"],
            "detail": "베이스라인(현재 값 기준 계산)이 안 되면 시나리오 비교도 할 수 없습니다",
            "baseline": baseline,
        }

    scenarios = []
    for field, value in known_rates.items():
        new_rates = {**known_rates, field: value * (1 + delta_pct)}
        result = decompose_goal(vertical, revenue_gap, new_rates)
        if result["status"] != "계산 완료":
            continue
        before = baseline["required_top_of_funnel"]
        after = result["required_top_of_funnel"]
        reduction_pct = round((before - after) / before * 100, 1) if before else 0
        scenarios.append(
            {
                "lever": field,
                "change": f"+{delta_pct * 100:.0f}%",
                "required_top_of_funnel_before": before,
                "required_top_of_funnel_after": after,
                "reduction_pct": reduction_pct,
            }
        )

    scenarios.sort(key=lambda s: s["reduction_pct"], reverse=True)
    return {
        "status": "계산 완료",
        "baseline_required_top_of_funnel": baseline["required_top_of_funnel"],
        "scenarios_ranked": scenarios,
        "note": (
            f"각 지표를 {delta_pct * 100:.0f}%씩 개선했을 때 필요 유입이 얼마나 줄어드는지 비교한 것 — "
            "실행 난이도·비용은 반영 안 됨, 순수 산수 기준 우선순위일 뿐"
        ),
    }


def estimate_profit_impact(revenue_gap: float, variable_cost_rate: float | None) -> dict:
    """매출 목표를 이익 기준으로 환산한다 (V5.0/X "Digital CFO"의 정직한 최소 버전).

    "매출을 얼마 늘려야 하는가"만 보면 안 되는 이유: 매출이 늘어도 원가가 그만큼
    같이 늘면 실제로 남는 돈(기여이익)은 훨씬 적을 수 있다. variable_cost_rate
    (매출 대비 변동비 비율, 0~1)를 업체가 실제로 알려준 경우에만 계산한다 —
    모르면서 "보통 이 정도"로 채우면 이익을 지어내는 것과 같다.

    고정비는 반영하지 않는다 — 그건 매출 증가분과 무관하게 이미 나가는 돈이라
    "이 매출 증가로 실제 남는 돈"을 보는 이 계산의 범위 밖이다.
    """

    if variable_cost_rate is None:
        return {
            "status": "데이터 부족",
            "detail": "variable_cost_rate(매출 대비 변동비 비율)를 알려주셔야 이익 기준으로 환산할 수 있습니다 — 매출 목표만으로는 실제로 남는 돈을 알 수 없습니다",
        }
    if not (0 <= variable_cost_rate <= 1):
        return {"status": "입력 오류", "detail": "variable_cost_rate는 0~1 사이 비율이어야 합니다"}

    contribution_margin_gap = revenue_gap * (1 - variable_cost_rate)
    return {
        "status": "계산 완료",
        "revenue_gap": revenue_gap,
        "variable_cost_rate": variable_cost_rate,
        "contribution_margin_gap": round(contribution_margin_gap),
        "note": "고정비 제외 — 매출 증가분 중 변동비 빼고 실제로 남는 금액(기여이익)만 계산한 것. 매출을 늘려도 이익이 그만큼 안 늘 수 있다는 걸 보여주는 최소 버전, LTV/CAC 등은 행동 이력이 있어야 해서 여기 없음",
    }


def main():
    example = decompose_goal(
        "restaurant",
        revenue_gap=20_000_000,
        known_rates={"avg_order_value": 30_000, "visit_conversion_rate": 0.6},
    )
    print(example)

    missing_example = decompose_goal("labor_firm", revenue_gap=10_000_000, known_rates={})
    print(missing_example)


if __name__ == "__main__":
    main()
