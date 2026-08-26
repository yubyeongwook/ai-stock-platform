# AI GROWTH OS — 확정 아키텍처 (사장님 설계, 2026-08-26)

**이 문서는 사장님이 직접 설계해서 확정한 최종 청사진이다.** 12단계 엔진 + 28개 에이전트 구조. 지금부터 이 문서를 기준으로 Phase 1부터 순서대로 코드화한다 — 매번 구조를 다시 짜지 않는다.

## 0. 이전 결정과의 관계 — 정직하게 짚고 간다

`docs/north-star-vision.md`에 사실상 같은 구조(12개 에이전트 버전)가 이미 한 번 검토됐고, 그때는 **"고객 6곳을 넘어서기 전까지는 짓지 않는다"**로 결론 냈었다 (엔지니어링에 몇 달 쏟다가 매출이 안 나는 걸 피하려고). 이번 결정은 그 판단을 사장님이 의식적으로 뒤집은 것이다 — 지금 이 문서가 최신이고 우선한다. 다만 그 문서의 핵심 우려(전부 한 번에 지으면 안 된다)는 이번 설계에도 그대로 반영돼 있다 — 사장님이 직접 "한 번에 전부 코드화하면 안 된다"고 명시했고, Phase 1부터 순서대로 간다.

## 1. 용어 정의 — "에이전트"가 실제로 뭘 의미하는지

이 세션 전체에서 지켜온 정직성 원칙을 계속 지킨다: 아래 28개 "Agent"는 대부분 **자율적으로 사고하는 존재가 아니라, 규칙 기반 로직 + (필요시) LLM 호출을 감싼 함수**다. `master_ai.py`, `business_dna.py`, `competitor_agent.py`가 이미 이 원칙으로 짜여 있다 — "AI가 판단한다"고 부르지만 실제로는 정해진 로직에 입력을 넣고 정해진 형식으로 결과를 받는 것. Phase가 올라가면서 일부(특히 Research/Strategy 계열)는 실제 LLM 추론 비중이 커지겠지만, 그럴 때도 "무엇을 자동 판단하고 무엇을 사람이 승인하는지"는 항상 코드와 문서에 명시한다 (10절 3단계 게이트 유지).

## 2. 전체 구조 (사장님 원안 그대로)

```
                         AI GROWTH OS COMMAND CENTER
                                    │
                    0. TENANT / COMPANY CORE (업체 등록·데이터·권한)
                                    │
                    1. BUSINESS INTELLIGENCE (업체·시장·고객·경쟁자 조사)
                                    │
                    2. INDUSTRY ROUTER (업종 자동 판별·전략 분기)
                                    │
                 ┌──────────────────┼──────────────────┐
               음식점              노무법인            병원/치과
                 └──────────────────┼──────────────────┘
                                    │
                    3. AI AGENT MANAGER (필요 Agent 자동 배치)
                                    │
                    4. CUSTOMER INTELLIGENCE (고객·잠재고객·구매심리)
                                    │
                    5. GROWTH STRATEGY ENGINE (매출목표→전략→우선순위)
                                    │
                    6. CONTENT / SEO ENGINE
                                    │
                    7. ADVERTISING ENGINE
                                    │
                    8. CONVERSION ENGINE
                                    │
                    9. CRM / RETENTION ENGINE
                                    │
                    10. REVENUE / KPI ENGINE
                                    │
                    11. AI OPTIMIZATION LOOP (성과분석→전략수정→재실행)
                                    │
                                    └──────────→ 반복
```

## 3. 기존 코드 ↔ 새 아키텍처 매핑

이 매핑이 핵심이다 — Phase 1~3은 사실 상당 부분 **이미 존재하는 코드를 정식 위치로 옮기고 스펙을 채우는 작업**이지, 전부 백지에서 새로 짓는 게 아니다.

| 새 아키텍처 컴포넌트 | 지금 코드 | 상태 |
|---|---|---|
| 0. Company Core | `clients/*.json` + `business_dna.py` | 부분 구현 — Phase 1에서 `company_core.py`로 정식화 |
| Command Center | `status_dashboard.py` | 미니 버전 존재 (6절 트리거 전까지 임시) |
| 1. Business Intelligence — Research Agent | 없음 (이번 세션에서 서초김치찌개·해안반점 리서치는 사람이 웹서치로 수동 수행) | Phase 4에서 착수 |
| 2. Industry Router | `business_dna.classify_business` | 구현됨 (3개 버티컬만) |
| ① Orchestrator Agent | `orchestrator.py` | 구현됨 (단순 버전) |
| ② Strategy Agent | `master_ai.py` (`propose_next_action`) | 구현됨 (규칙 기반 룩업) |
| ③ QA/Compliance Agent | `business_dna.py`의 banned_terms + `vertical_active` 게이트 | 구현됨 |
| ⑤ Competitor Agent | `competitor_agent.py` | 구현됨 (known_competitors 없으면 거부) |
| ⑩ SEO Agent (로컬) | `local_place_agent.py` | 구현됨 |
| ⑩ SEO Agent (기술) | `adsense_readiness_agent.py` | 구현됨 (5개 실측 진단) |
| ⑫ Content Creation Agent | `blog_content_agent.py` + `integrations/llm_writer.py` | 구현됨 (API 키 있으면 본문까지) |
| ⑯⑰ Ads/Campaign Agent | `integrations/meta_ads.py` | 부분 구현 (조회만, 집행은 사람 승인) |
| ㉒ CRM Agent | `integrations/kakao_alimtalk.py` + `orchestrator.send_review_reminder` | 구현됨 |
| ㉖ Analytics Agent | `integrations/ga4_client.py` + `status_dashboard.py` | 부분 구현 |
| 나머지 (④⑥⑦⑧⑨⑪⑬⑭⑮⑱⑲⑳㉑㉓㉔㉕㉗㉘) | 없음 | Phase별로 순서대로 착수 |

## 4. 3단계 실행 게이트 (기존 원칙 그대로 유지, 전체 OS에 적용)

이미 여러 모듈에서 지켜온 원칙을 전체 OS 설계에 명시적으로 승격한다.

| 등급 | 범위 | 예시 |
|---|---|---|
| 🟢 AI 자동 실행 | 시장조사, 경쟁사 조사(자료 있을 때), 키워드 조사, 콘텐츠 초안, 데이터 분석, KPI 리포트 | `blog_content_agent`, `master_ai.diagnose_bottleneck` |
| 🟡 AI 생성 + 사람 승인 | 광고 캠페인 실행/예산 변경, 대량 콘텐츠 게시, 고객 메시지 발송, 가격 변경 | `master_ai.propose_next_action`(승인 대기 상태 반환), `integrations/meta_ads.py`(집행 전 사람 승인) |
| 🔴 사람 최종 결정 | 법적/의료적/노무 판단, 계약, 고액 광고비 집행, 민감정보 처리, 분쟁 대응 | `business_dna.py`의 `active: False` 게이트(의료 등) |

## 5. 업종별 퍼널 차이 (참고, 사장님 원안)

- **음식점**: 지역검색→지도→메뉴→후기→방문→재방문→단골→추천. KPI: 방문객·예약·객단가·재방문·리뷰·테이블회전·신규고객비용
- **노무법인**: 검색→문제인지→정보탐색→전문성확인→상담→계약→장기고객. KPI: 상담문의·상담전환율·계약전환율·계약가치·고객유지·리드당비용 (대량방문보다 고품질 리드 중심)
- **병원/치과**: 지역검색→증상검색→병원비교→신뢰형성→예약→내원→치료→재방문. **의료광고·개인정보 QA 게이트를 별도로 강하게 적용** — `business_dna.py`에서 `medical_general`/`dental`이 `active: False`인 이유가 바로 이것, Phase 확장 전 반드시 법 조문 검증

## 6. 개발 순서 (사장님 확정, 변경 없이 그대로 채택)

| Phase | 내용 | 상태 |
|---|---|---|
| 1 | Company Core / Command Center | 진행 중 — `company_core.py`(로직) + `db.py`/`db_models.py`/`api_server.py`(로컬 DB·API 스켈레톤) 구현됨 |
| 2 | Industry Router | 기초 구현 존재, 고도화 예정 |
| 3 | AI Agent Manager | 미착수 |
| 4 | Business Intelligence + Customer Intelligence | 미착수 |
| 5 | Growth Strategy Engine | 기초 구현 존재(`master_ai.py`) + Revenue Equation Engine/Goal Decomposer(`revenue_engine.py`, `docs/ai-growth-os-future-vision.md`에서 조기 도입) |
| 6 | SEO + Content Engine | 부분 구현 존재 |
| 7 | Advertising + Campaign Engine | 부분 구현 존재 |
| 8 | Conversion + Landing Page Engine | 미착수 |
| 9 | CRM + Retention + Referral Engine | 부분 구현 존재 |
| 10 | KPI + Revenue + Attribution Engine | 부분 구현 존재(`status_dashboard.py`) |
| 11 | Automation / Connector Layer | 부분 구현 존재(`integrations/`) |
| 12 | AI Optimization / Autonomous Growth Loop | 미착수 |

**중요**: 12개의 독립 프로그램이 아니라 **하나의 OS 안에 12개 엔진이 연결되는 구조**다 — 새 Phase를 지을 때마다 이 문서의 매핑 표(3절)를 먼저 갱신해서 중복 구현을 피한다.

## 7. 실제 기술 구현 범위 — 2026-08-26 확정

사장님이 Next.js + FastAPI + PostgreSQL + Redis + Vector DB + Connector 6종 + Workflow Engine까지 포함한 전체 기술 스택을 상세 설계했다(원안 그대로 아래 보존). 다만 실행 범위는 사장님이 직접 확인해준 대로 **"이 저장소 안에 로컬 DB로 스켈레톤만"**으로 좁혀서 지금 착수한다 — 실제 배포 인프라(Postgres 호스팅, Redis, 도메인, 계정·과금)는 짓지 않는다.

**지금 구현된 것:**
- `db.py` — SQLAlchemy 엔진/세션. 기본값은 로컬 SQLite(`growth_os.db`, 이 저장소 안에서만 존재, git에는 안 올라감). `DATABASE_URL` 환경변수만 바꾸면 나중에 Postgres로 전환 가능하게 추상화는 해뒀지만, 지금 실제로 Postgres에 연결하지는 않는다
- `db_models.py` — Company Core를 담는 `companies` 테이블. `clients/*.json` 스키마를 그대로 컬럼으로 옮긴 것
- `api_server.py` — FastAPI 앱. `/companies` CRUD 4개 엔드포인트, `company_core.build_company_profile()`을 그대로 재사용. `uvicorn api_server:app`으로 로컬에서만 띄운다 — 배포 안 함
- `import_clients_to_db.py` — 기존 `clients/*.json` 8개를 DB로 옮기는 마이그레이션 스크립트 (slug 기준 upsert, 반복 실행 안전)
- 테스트 12개 추가(company_core 5개 + api_server 7개), 전체 스위트 96개 통과

**아직 안 만든 것 (정직하게 밝힘):**
- Next.js 프론트엔드, Command Center UI — 없음
- 인증/권한 시스템 — 없음
- Agent Registry (DB 테이블로 Agent 목록 관리) — 없음
- Workflow Engine (COMPANY_CREATED → ... → DASHBOARD_READY 같은 이벤트 체인) — 없음
- Redis/Queue, Vector DB, Object Storage — 없음
- Connector Layer(Naver/Google/Meta/Website/CRM/예약) — 없음, `integrations/`의 카카오·메타·GA4 개별 연동이 사실상의 초기 버전
- 실제 배포(Vercel/Render/Supabase 등 새 계정·과금) — 없음

**다음 착수 순서 제안** (사장님 원안의 Phase 2~3에 해당): Industry Router를 DB의 `industry_profiles` 테이블로 정식화하고, `business_dna.py`의 3개 하드코딩 프로필을 거기서 읽어오게 바꾸는 것 — 이게 "업종 추가할 때마다 코드 안 고치고 DB에 행만 추가" 원칙을 실제로 만족시키는 첫 단계다.

### 참고 — 사장님 원안 전체 (기술 스택·Agent 인터페이스·Event 기반 설계·최종 화면 목업 등)

원안 전문은 이 리포지토리의 대화 이력에 있다 — 여기 다시 옮겨적지 않고, 실제 구현이 각 Phase에 도달할 때마다 이 섹션에 해당 부분을 발췌해 반영하는 방식으로 관리한다(문서가 너무 길어지는 것을 피하기 위함). 핵심 원칙 5가지만 여기 남겨둔다:
1. Agent마다 별도 프로그램을 만들지 않는다 — Agent + Industry Profile + Business DNA + Goal = 업체별 행동 (Config 조합)
2. Agent Output은 항상 구조화된 형식(status/confidence/findings/recommendations/risk_level/requires_approval)으로 표준화한다
3. Agent끼리 직접 호출하지 않는다 — 전부 Workflow Engine/Orchestrator를 거친다
4. 공통 Engine 80% + 업종별 Profile/Rule/Template 20%를 목표로 한다
5. 가장 중요한 5개: Business DNA, Industry Router, Agent Orchestrator, Revenue/KPI Engine, Optimization Loop
