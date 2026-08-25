"""성과 로그 — 3단계(업종 플레이북 자산화)의 재료를 실제로 쌓는 곳.

지금 `master_ai.py`의 벤치마크는 전부 가정치다. 이 모듈은 실제 파일럿에서
나온 진짜 숫자를 쌓는 곳이고, 데이터가 쌓이면 그걸로 벤치마크를 실측치로
바꾸는 게 3단계의 실제 내용이다. 지금은 로그를 쌓는 틀만 있고, 안에 든
데이터는 아직 0건이다 — 이 파일 자체가 "플레이북 완성"이 아니라 "플레이북을
만들 재료를 받을 그릇"이다.
"""

import json
from datetime import datetime
from pathlib import Path

LOG_PATH = Path("performance_log.jsonl")


def record_result(client_slug: str, vertical: str, metrics: dict, note: str = "") -> dict:
    """실제 성과 지표 1건을 로그에 追加한다. metrics는 master_ai.py의 지표 키와 맞춘다
    (impressions/ctr/conversion_rate/return_rate 등)."""

    entry = {
        "timestamp": datetime.now().isoformat(),
        "client_slug": client_slug,
        "vertical": vertical,
        "metrics": metrics,
        "note": note,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def load_results(vertical: str | None = None) -> list[dict]:
    """쌓인 로그를 읽는다. vertical을 주면 그 업종만 필터링."""

    if not LOG_PATH.exists():
        return []

    results = []
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if vertical is None or entry["vertical"] == vertical:
                results.append(entry)
    return results


def suggest_benchmark_update(vertical: str, metric: str) -> dict:
    """특정 업종·지표의 실측 중앙값을 계산해, master_ai.py 벤치마크 교체를 제안한다.

    최소 3건 이상 쌓여야 의미 있는 제안으로 취급한다 — 그 전엔 표본이 너무 적어
    가정치보다 못할 수 있다.
    """

    results = load_results(vertical)
    values = [r["metrics"][metric] for r in results if metric in r["metrics"]]

    if len(values) < 3:
        return {
            "ready": False,
            "reason": f"{vertical}/{metric} 데이터 {len(values)}건 — 최소 3건 필요, 아직 가정치 유지 권장",
        }

    values.sort()
    median = values[len(values) // 2]
    return {
        "ready": True,
        "vertical": vertical,
        "metric": metric,
        "sample_size": len(values),
        "suggested_benchmark": median,
        "note": "master_ai.py의 FUNNEL_STAGES 벤치마크를 이 값으로 교체 검토",
    }


def main():
    print(f"쌓인 로그: {len(load_results())}건")
    for vertical in ("restaurant", "labor_firm"):
        print(suggest_benchmark_update(vertical, "conversion_rate"))


if __name__ == "__main__":
    main()
