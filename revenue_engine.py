"""revenue_engine.py — Revenue Equation Engine + Goal Decomposer.

`docs/ai-growth-os-v3-vision.md` 6·7절의 최소 정직한 버전. 업종별 매출 방정식으로
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
