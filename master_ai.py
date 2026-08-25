"""Master AI — 성과 데이터를 보고 이번 주기에 뭘 우선할지 정한다 (퍼널 병목 탐지).

`docs/client-revenue-funnel.md`의 퍼널(노출×클릭률×전환율×재방문율) 각 단계를
벤치마크와 비교해, 상대적으로 가장 낮은 단계를 병목으로 지목하고 그 단계를
담당하는 에이전트에게 우선순위를 배정한다.

정직하게 말하면: 이건 학습된 판단이 아니라 **규칙 기반 병목 탐지**다.
벤치마크는 `docs/client-revenue-funnel.md` 2절의 가정치를 그대로 썼다 —
실제 파일럿 데이터가 쌓이면 이 벤치마크를 업종별 실측 중앙값으로 반드시
교체해야 의미가 생긴다. 지금 이 모듈의 가치는 "판단 자체"가 아니라
"판단하는 방법을 코드로 고정해뒀다는 것" — 사람이 매번 감으로 우선순위를
정하는 대신, 같은 기준으로 반복 가능하게 만든 것이다.
"""

# 퍼널 단계, 측정 지표 키, 벤치마크(가정치), 담당 에이전트 — docs/client-revenue-funnel.md 2절 기준
FUNNEL_STAGES = [
    {"stage": "노출", "metric": "impressions", "benchmark": 500, "owner_agents": ["블로그 콘텐츠", "로컬 SEO"]},
    {"stage": "클릭률", "metric": "ctr", "benchmark": 0.03, "owner_agents": ["블로그 최적화", "로컬 SEO"]},
    {"stage": "전환율", "metric": "conversion_rate", "benchmark": 0.10, "owner_agents": ["랜딩페이지 카피", "CRO"]},
    {"stage": "재방문율", "metric": "return_rate", "benchmark": 0.20, "owner_agents": ["리뷰·리텐션"]},
]


def diagnose_bottleneck(metrics: dict) -> dict:
    """각 단계의 (실측/벤치마크) 비율을 계산해 가장 낮은 단계를 병목으로 지목한다.

    metrics 예시: {"impressions": 320, "ctr": 0.025, "conversion_rate": 0.08}
    측정 안 된 지표(그 채널을 아직 안 붙인 경우)는 건너뛴다.
    """

    scored = []
    for stage in FUNNEL_STAGES:
        value = metrics.get(stage["metric"])
        if value is None:
            continue
        ratio = (value / stage["benchmark"]) if stage["benchmark"] else 0
        scored.append({**stage, "value": value, "ratio": ratio})

    if not scored:
        return {"bottleneck": None, "reason": "측정된 지표가 없음 — 최소 1개 채널 연동 필요"}

    bottleneck = min(scored, key=lambda s: s["ratio"])
    return {
        "bottleneck": bottleneck["stage"],
        "ratio": round(bottleneck["ratio"], 2),
        "recommended_agents": bottleneck["owner_agents"],
        "reason": f"{bottleneck['stage']}이(가) 벤치마크 대비 {round(bottleneck['ratio'] * 100)}%로 가장 낮음",
        "all_stages": [{"stage": s["stage"], "ratio": round(s["ratio"], 2)} for s in scored],
    }


def next_cycle_priority(client_name: str, metrics: dict) -> dict:
    """고객사 하나에 대해 다음 주기 우선순위를 결정한다. 사람 승인 없이 실행까지는 안 간다(레벨 2 게이트)."""

    diagnosis = diagnose_bottleneck(metrics)
    return {"client": client_name, "diagnosis": diagnosis, "status": "사람 승인 대기 (자동 실행 아님)"}


def main():
    examples = [
        ("예시식당", {"impressions": 320, "ctr": 0.025, "conversion_rate": 0.08, "return_rate": 0.10}),
        ("예시노무법인", {"impressions": 900, "ctr": 0.05, "conversion_rate": 0.03}),
    ]
    for name, metrics in examples:
        print(next_cycle_priority(name, metrics))


if __name__ == "__main__":
    main()
