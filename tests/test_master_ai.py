from master_ai import diagnose_bottleneck, next_cycle_priority, propose_next_action


def test_no_metrics_returns_no_bottleneck():
    result = diagnose_bottleneck({})
    assert result["bottleneck"] is None


def test_picks_lowest_ratio_stage():
    metrics = {"impressions": 1000, "ctr": 0.03, "conversion_rate": 0.03}  # 전환율이 벤치마크 0.10 대비 가장 낮음(30%)
    result = diagnose_bottleneck(metrics)
    assert result["bottleneck"] == "전환율"
    assert result["recommended_agents"] == ["랜딩페이지 카피", "CRO"]


def test_ignores_unmeasured_stages():
    metrics = {"impressions": 1000}  # ctr/conversion_rate/return_rate 없음
    result = diagnose_bottleneck(metrics)
    assert result["bottleneck"] == "노출"
    assert len(result["all_stages"]) == 1


def test_next_cycle_priority_never_auto_executes():
    result = next_cycle_priority("업체", {"impressions": 100})
    assert "승인" in result["status"]


def test_propose_next_action_matches_bottleneck_stage():
    metrics = {"impressions": 1000, "ctr": 0.03, "conversion_rate": 0.03}
    result = propose_next_action("업체", metrics)
    assert result["diagnosis"]["bottleneck"] == "전환율"
    assert len(result["candidate_actions"]) > 0
    assert "승인" in result["status"]


def test_propose_next_action_empty_when_no_bottleneck():
    result = propose_next_action("업체", {})
    assert result["candidate_actions"] == []


def test_propose_next_action_tags_every_candidate_with_a_portfolio_tier():
    metrics = {"impressions": 1000, "ctr": 0.03, "conversion_rate": 0.03}
    result = propose_next_action("업체", metrics)
    tagged = result["candidate_actions_tagged"]
    assert len(tagged) == len(result["candidate_actions"])
    for item in tagged:
        assert item["portfolio_tier"] in {"안전", "핵심", "실험"}


def test_propose_next_action_tagged_list_empty_when_no_bottleneck():
    result = propose_next_action("업체", {})
    assert result["candidate_actions_tagged"] == []
