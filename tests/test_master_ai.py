from master_ai import diagnose_bottleneck, next_cycle_priority


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
