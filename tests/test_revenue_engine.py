from revenue_engine import decompose_goal, estimate_profit_impact, what_if


def test_unsupported_vertical_returns_clear_status():
    result = decompose_goal("beauty", revenue_gap=1_000_000, known_rates={})
    assert result["status"] == "미지원 업종"


def test_zero_gap_means_goal_already_met():
    result = decompose_goal("restaurant", revenue_gap=0, known_rates={})
    assert result["status"] == "목표 달성됨"


def test_negative_gap_is_input_error():
    result = decompose_goal("restaurant", revenue_gap=-500, known_rates={})
    assert result["status"] == "입력 오류"


def test_missing_rates_refuses_to_guess():
    result = decompose_goal("restaurant", revenue_gap=10_000_000, known_rates={})
    assert result["status"] == "데이터 부족"
    assert "객단가" in result["missing_fields"]
    assert "방문전환율(유입 대비 실제 방문/주문 비율)" in result["missing_fields"]


def test_partial_rates_still_refuses():
    result = decompose_goal(
        "restaurant", revenue_gap=10_000_000, known_rates={"avg_order_value": 20_000}
    )
    assert result["status"] == "데이터 부족"
    assert result["missing_fields"] == ["방문전환율(유입 대비 실제 방문/주문 비율)"]


def test_full_rates_computes_exact_chain():
    result = decompose_goal(
        "restaurant",
        revenue_gap=30_000_000,
        known_rates={"avg_order_value": 30_000, "visit_conversion_rate": 0.5},
    )
    assert result["status"] == "계산 완료"
    # 30,000,000 / 30,000 = 1000건 -> / 0.5 = 2000명
    assert result["required_top_of_funnel"] == 2000.0


def test_labor_firm_three_stage_chain():
    result = decompose_goal(
        "labor_firm",
        revenue_gap=100_000_000,
        known_rates={
            "avg_contract_value": 5_000_000,
            "contract_conversion_rate": 0.5,
            "consult_conversion_rate": 0.4,
        },
    )
    assert result["status"] == "계산 완료"
    # 100,000,000 / 5,000,000 = 20건 -> /0.5 = 40상담 -> /0.4 = 100 Lead
    assert result["required_top_of_funnel"] == 100.0


def test_dental_four_stage_chain_all_present():
    result = decompose_goal(
        "dental",
        revenue_gap=50_000_000,
        known_rates={
            "avg_treatment_value": 1_000_000,
            "treatment_conversion_rate": 0.5,
            "visit_rate": 0.8,
            "reservation_conversion_rate": 0.25,
        },
    )
    assert result["status"] == "계산 완료"
    assert result["required_top_of_funnel"] > 0


def test_what_if_refuses_without_baseline_data():
    result = what_if("restaurant", 10_000_000, known_rates={})
    assert result["status"] == "데이터 부족"


def test_what_if_ranks_scenarios_and_shows_reduction():
    result = what_if(
        "restaurant",
        30_000_000,
        known_rates={"avg_order_value": 30_000, "visit_conversion_rate": 0.5},
    )
    assert result["status"] == "계산 완료"
    assert len(result["scenarios_ranked"]) == 2
    for scenario in result["scenarios_ranked"]:
        assert scenario["required_top_of_funnel_after"] < scenario["required_top_of_funnel_before"]
        assert scenario["reduction_pct"] > 0


def test_what_if_custom_delta_pct():
    result = what_if(
        "restaurant",
        30_000_000,
        known_rates={"avg_order_value": 30_000, "visit_conversion_rate": 0.5},
        delta_pct=0.2,
    )
    assert all(s["change"] == "+20%" for s in result["scenarios_ranked"])


def test_profit_impact_refuses_without_cost_rate():
    result = estimate_profit_impact(10_000_000, variable_cost_rate=None)
    assert result["status"] == "데이터 부족"


def test_profit_impact_rejects_out_of_range_rate():
    result = estimate_profit_impact(10_000_000, variable_cost_rate=1.5)
    assert result["status"] == "입력 오류"


def test_profit_impact_computes_contribution_margin():
    result = estimate_profit_impact(10_000_000, variable_cost_rate=0.4)
    assert result["status"] == "계산 완료"
    assert result["contribution_margin_gap"] == 6_000_000
