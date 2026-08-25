import performance_log


def test_record_and_load_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(performance_log, "LOG_PATH", tmp_path / "log.jsonl")

    performance_log.record_result("client-a", "restaurant", {"conversion_rate": 0.09})
    performance_log.record_result("client-b", "labor_firm", {"conversion_rate": 0.05})

    all_results = performance_log.load_results()
    assert len(all_results) == 2

    restaurant_only = performance_log.load_results("restaurant")
    assert len(restaurant_only) == 1
    assert restaurant_only[0]["client_slug"] == "client-a"


def test_load_results_empty_when_no_log_file(tmp_path, monkeypatch):
    monkeypatch.setattr(performance_log, "LOG_PATH", tmp_path / "nonexistent.jsonl")
    assert performance_log.load_results() == []


def test_suggest_benchmark_update_needs_minimum_sample(tmp_path, monkeypatch):
    monkeypatch.setattr(performance_log, "LOG_PATH", tmp_path / "log.jsonl")

    performance_log.record_result("a", "restaurant", {"conversion_rate": 0.08})
    performance_log.record_result("b", "restaurant", {"conversion_rate": 0.12})

    result = performance_log.suggest_benchmark_update("restaurant", "conversion_rate")
    assert result["ready"] is False


def test_suggest_benchmark_update_ready_at_three_samples(tmp_path, monkeypatch):
    monkeypatch.setattr(performance_log, "LOG_PATH", tmp_path / "log.jsonl")

    for value in (0.08, 0.10, 0.12):
        performance_log.record_result("client", "restaurant", {"conversion_rate": value})

    result = performance_log.suggest_benchmark_update("restaurant", "conversion_rate")
    assert result["ready"] is True
    assert result["suggested_benchmark"] == 0.10
    assert result["sample_size"] == 3
