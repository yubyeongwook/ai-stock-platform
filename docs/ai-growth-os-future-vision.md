# AI GROWTH OS — 장기 비전 (V3.0 + V5.0 + X, 지금 안 지음, 사장님 설계, 2026-08-26)

**이 문서는 북극성이다. Phase로 안 잡혀있고, 지금 착수 대상이 아니다.** `docs/ai-growth-os-architecture.md`(현재 실제로 짓고 있는 12단계 구조)와 이 문서를 혼동하지 말 것 — 그쪽이 "지금 순서대로 짓는 것", 이 문서는 "데이터·규모가 쌓였을 때 참고할 최종형".

## 왜 지금 안 짓는지 (정직하게)

사장님이 이 V3.0을 제시했을 때(Digital Twin, Event Mesh, AI Executive Board 토론, Causal Intelligence, Customer Propensity Engine, Confidence Engine 등), 검토 결과 대부분의 컴포넌트가 **실제 데이터(수백~수천 건의 고객 행동 이력, 몇 달치 캠페인 실험 결과)가 있어야만 정직하게 구현 가능**하다는 결론을 내렸다:

- Causal Intelligence, Customer Propensity Engine — 실제 행동 이력으로 학습해야 하는데 지금 그 데이터가 없음. 지금 만들면 숫자를 지어내는 것과 같음
- AI Executive Board 토론(CMO/CFO/CRO/CCO가 논의) — 근거 데이터 없이 LLM 하나가 여러 페르소나로 자문자답하는 것에 불과, "AI 임원진이 논의해서 결정했다"고 파는 건 이 프로젝트 전체가 지켜온 "확신 없는 걸 확신 있게 말하지 않는다" 원칙과 충돌
- Confidence Engine(93% 신뢰도 표시) — 캘리브레이션된 모델 없이 숫자만 붙이면 거짓 정밀도

`master_ai.py`가 이미 "벤치마크는 가짜다, 실제 파일럿 데이터 쌓이면 교체해야 한다"고 코드에 정직하게 남겨둔 것과 같은 이유다. 고객사가 6곳을 넘어 실제 행동·매출 데이터가 쌓이는 시점(`docs/north-star-vision.md`의 트리거와 동일)에 이 문서를 다시 꺼내서, 그때 실제로 뒷받침 가능한 부분부터 순서대로 착수한다.

## 지금 이미 가져온 것 (예외)

아래 2개는 학습된 데이터가 아니라 **순수 산수**라서 데이터 없이도 정직하게 지금 구현 가능하다고 판단해 먼저 가져왔다 — `revenue_engine.py` 참고.
- **Revenue Equation Engine** (V3.0 6절) — 업종별 매출 방정식
- **Goal Decomposer** (V3.0 7절) — 목표매출을 역산해 필요 유입/전환 계산. 단, 업체가 실제로 측정한 전환율만 쓰고, 모르는 값을 업계 평균으로 대신 채우지 않는다(그건 이 업체의 실제 숫자가 아니므로) — 값이 없으면 "측정 필요"로 명시하고 계산을 중단한다.

## 원문 전체 보존

아래는 사장님이 제시한 V3.0 설계 원문이다(46개 절, Digital Twin / Event Mesh / Revenue Equation Engine / Goal Decomposer / Growth Bottleneck Detection 3.0 / Margin Intelligence / CLV Engine / Customer Propensity Engine / Next Best Action / Offer Intelligence / Channel Intelligence / AI Budget Allocation / Attribution Engine / Causal Intelligence / Experiment OS / Failure Intelligence / Strategy Memory / AI Executive Board / AI Debate Engine / Decision Ledger / Confidence Engine / Risk Matrix / Self-Healing / Agent Observability / Unit Economics Engine / Multi-Tenant / Cross-Industry Intelligence / Industry Benchmark Engine / Growth Score / Growth Roadmap / AI Operating Calendar / 7 Brain 구조 / 12 Core + 7 Brain + 3 Control Layer 최종 구조). 세션 대화 이력에 원문 전체가 남아있으므로 여기 다시 옮겨적지 않고, **실제 구현이 각 항목에 도달할 때 그 부분만 발췌해서 코드화**하는 방식으로 관리한다 — 문서가 실행 계획과 분리된 채 비대해지는 것을 막기 위함.

## 착수 순서 후보 (데이터가 쌓이면, 우선순위 순)

1. Revenue Equation Engine + Goal Decomposer — ✅ 완료 (`revenue_engine.py`)
2. What-If / Counterfactual Engine(V5.0 8·35·36절의 정직한 버전) — ✅ 완료 (`revenue_engine.what_if()`). 순수 산수(민감도 분석)라 데이터 없이도 정직함 — 실행 난이도·비용은 반영 안 한다고 명시
3. Growth Portfolio 태깅(V5.0 9절) — ✅ 완료 (`master_ai.ACTION_PORTFOLIO_TIER`). 데이터 계산이 아니라 액션 성격에 따른 사람의 편집적 분류라고 명시
4. Growth Bottleneck Detection 고도화(Volume/Conversion/Revenue/Margin/Retention 동시 판단) — `master_ai.py` 확장, 실측 지표 여러 개 있으면 가능
5. Margin Intelligence — 원가·광고비 데이터가 client 브리프에 들어오면 가능
6. Decision Ledger — 이건 데이터가 없어도 가능(그냥 의사결정 기록 테이블), 다만 지금은 의사결정 자체가 적어 가치가 낮음. Phase 3(Agent Manager) 이후 자연스럽게 필요해지면 추가
7. 그 외 전부(Digital Twin, Event Mesh, AI Executive Board 토론, Causal/Propensity Engine, Knowledge Graph+RAG, Truth Layer, Agent Reputation System 등 V3·V5의 나머지) — 고객 6곳+ 실행 데이터 쌓인 뒤 재검토

## V5.0 원문도 여기 같은 방식으로 보존

사장님이 이어서 제시한 "AI GROWTH OS V5.0"(43절, Business Digital Twin 고도화·Growth Constraint Engine·Counterfactual Engine·Growth Portfolio Engine·Strategic Kill Engine·AI Board 반박 구조·Prediction Accuracy·Agent Reputation·Knowledge Graph+RAG·Truth Layer·Business Stress Test·Early Warning System·Opportunity Radar·AI Growth Autopilot 등) 원문도 V3와 같은 원칙으로 관리한다 — 세션 대화 이력에 원문이 남아있고, 여기 다시 옮겨적지 않는다. V3와 마찬가지로 "정교함"과 "지금 지을 수 있음"의 격차가 더 벌어졌다는 게 검토 결론 — 대부분 다개월치 행동·실험 데이터가 필요하다.

## X ("Autonomous Business Growth Intelligence Platform") — 마지막 버전, 사장님이 직접 "마지막"이라 명명

10개 층 구조(HUMAN COMMAND / AUTOPILOT / LEARNING / EXECUTION / STRATEGY / REVENUE / INTELLIGENCE / DIGITAL TWIN / AGENT·SKILL / DATA·EVENT), Growth Strategy Competition(전략 후보 수십 개 경쟁), Growth Capital Allocation Engine, Strategy Tree/Genome, Industry Pattern Intelligence, AI Freedom Level(0~5), Self-Improvement Engine, Digital CFO, Business Survival/Scale Mode, "8가지 최종 고도화 기준" 등 20절. 원문은 세션 대화 이력 참고, 여기 다시 옮겨적지 않음.

**이번에도 같은 필터 결과**: 대부분(Strategy Competition의 성공확률·예상이익 추정, Strategy Tree/Genome, Industry Pattern Intelligence, Self-Improvement Engine)은 실행 이력·확률 데이터가 있어야 정직함. Self-Improvement Engine(AI가 자기 코드를 수정)은 데이터 문제를 떠나 **안전 설계(샌드박스·테스트·보안·승인 파이프라인) 자체가 이 프로젝트 규모에서 감당하기 어려운 별도 프로젝트급 작업**이라 데이터가 쌓여도 신중하게 접근해야 함 — 우선순위 최하위로 남겨둠.

**이번에 가져온 것 2개** (순수 로직/설정, 데이터 불필요):
- **AI Freedom Level 0~5** (X 10·11절) — ✅ 완료 (`business_dna.py`의 `FREEDOM_LEVELS`, `default_freedom_level`, `build_business_dna()`의 `explicit_freedom_level` 파라미터). 새 개념이 아니라 이미 있던 3단계 게이트(🟢자동/🟡승인/🔴사람)를 업종별 기본값 + 클라이언트별 override가 가능한 숫자로 명시화한 것. `vertical_active=False`인 업종은 freedom_level을 무조건 0으로 강제(모순 방지)
- **Digital CFO의 최소 버전** (X 13·14절) — ✅ 완료 (`revenue_engine.estimate_profit_impact()`). "매출 목표"를 "실제 남는 돈(기여이익)" 기준으로 환산. `variable_cost_rate`(매출 대비 변동비 비율)를 업체가 실제로 알려준 경우에만 계산, 없으면 "데이터 부족". CAC/LTV/현금흐름은 행동·거래 이력이 필요해서 여기 포함 안 함 — 원가율만 아는 선에서 할 수 있는 딱 그만큼만

## 패턴 정리 (V3 → V5 → X)

버전이 올라갈수록 "정교함"과 "지금 지을 수 있음"의 격차가 계속 벌어졌다 — 매번 채택된 건 1~2개뿐이었다. 사장님이 X를 "마지막"이라 명명했으므로, 다음 단계는 새 버전 설계가 아니라 **지금까지 가져온 조각들(Goal Decomposer, What-If, Portfolio 태깅, Freedom Level, Digital CFO)을 실제 클라이언트(서초김치찌개·해안반점)에 적용해 검증**하는 것으로 넘어간다.
