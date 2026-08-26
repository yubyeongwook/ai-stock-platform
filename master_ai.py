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


# 병목 단계 -> 구체적으로 뭘 해보라고 제안할지. "재전략 수립"이라고 부르지만 실제로는
# 병목 단계별 고정 액션 목록에서 골라 보여주는 규칙 기반 룩업이다 — AI가 새로운 전략을
# 만들어내는 게 아니라, 사람이 승인할 후보를 미리 정리해두는 것뿐이다.
ACTIONS_BY_STAGE = {
    "노출": [
        "블로그 발행 빈도를 늘린다 (주 X회 -> Y회)",
        "롱테일 키워드(경쟁 적은 구체적 검색어)로 신규 글 추가",
        "인스타그램/카드뉴스 배포 채널 추가",
    ],
    "클릭률": [
        "제목(헤드라인) 포맷을 4U 공식 중 다른 유형으로 교체해 A/B 비교",
        "썸네일/대표 이미지 교체",
    ],
    "전환율": [
        "CTA 문구를 명확한 행동 지시형으로 교체",
        "랜딩 페이지 첫 화면에 핵심 혜택 재배치",
        "리뷰·후기 섹션 강화(있는 그대로의 실제 후기만)",
    ],
    "재방문율": [
        "카카오 알림톡 리마인드 발송 주기 점검",
        "재방문 유도 혜택(실제 존재하는 것만) 콘텐츠에 명시",
    ],
}


def propose_next_action(client_name: str, metrics: dict) -> dict:
    """병목 진단에 더해 "이번 주기에 뭘 해볼지" 후보까지 제안한다. next_cycle_priority()보다
    한 단계 더 구체적이지만, 실행은 여전히 사람이 승인해야 한다(레벨 2 게이트 유지) —
    "AI 재전략 수립"은 새 전략을 창작하는 게 아니라 정해진 액션 후보 중 관련된 것만
    골라 보여주는 규칙 기반 매칭이다."""

    diagnosis = diagnose_bottleneck(metrics)
    stage = diagnosis.get("bottleneck")
    candidate_actions = ACTIONS_BY_STAGE.get(stage, [])

    return {
        "client": client_name,
        "diagnosis": diagnosis,
        "candidate_actions": candidate_actions,
        "status": "사람 승인 대기 (자동 실행 아님) — 후보 중 하나를 사람이 선택해야 함",
    }


def main():
    examples = [
        ("예시식당", {"impressions": 320, "ctr": 0.025, "conversion_rate": 0.08, "return_rate": 0.10}),
        ("예시노무법인", {"impressions": 900, "ctr": 0.05, "conversion_rate": 0.03}),
    ]
    for name, metrics in examples:
        print(next_cycle_priority(name, metrics))


if __name__ == "__main__":
    main()
