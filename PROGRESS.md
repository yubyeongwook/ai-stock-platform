# 진행 기록

세션마다 최상단에 현황판을 갱신한다. 카테고리: 한것 / 진행중 / 할것 / 미정 / 내가할거(사장님).

---

## 현황판 (2026-08-25 기준)

### ✅ 한 것 (완료)

**1단계 코어 엔진**
- 9개 에이전트 + `content_playbook.py`(카피라이팅·SEO·전환심리학 노하우) + `business_dna.py`(업종 자동판별) + `master_ai.py`(퍼널 병목 진단)
- 카카오·메타·GA4·LLM 연동 코드 (크리덴셜 없으면 안 죽고 "미설정" 표시)
- 테스트 53개, GitHub Actions CI 통과
- **실제 API 키로 GitHub Actions에서 진짜 블로그 본문 생성 성공** (서초김치찌개) — 1차 생성에서 AI가 확인 안 된 운영방식("묵은지 자체 숙성" 등)을 지어낸 걸 발견·사장님이 사실 아님을 확인 → `integrations/llm_writer.py`에 "사실 지어내기 금지" 규칙 추가해 재수정, 재생성 결과 확인 완료(56개 테스트 통과)
- 치과 등 미검증 버티컬 코드 레벨 차단(`override_vertical_hold` 없으면 실행 자체가 안 됨)

**2~6단계 뼈대** (데이터·인프라 없이 틀만)
- 견적서 템플릿, `performance_log.py`, `status_dashboard.py`, SaaS DB 스키마 초안, 업종 프로필 4개(비활성) 추가

**운영 인프라**
- 브랜드 **매출엔진**, 가격정책(**사업자등록 완료 전까지 무료**, 등록 후 Phase1 정가 90만원/월~), 사업자등록 방향(간이과세자 추천)
- 계약서 템플릿(노무법인 특약, 공인노무사법 27조의2 실조문 확인)
- PR #1 main 머지, CI/CD 워크플로 2개 가동 중

**파일럿 확보**
- 음식점(서초김치찌개), 노무사무실(소속) — 2곳 접근권한 확보
- **매출엔진 자신도 3번째 클라이언트로 등록** (`clients/maechul-engine.json`) — 루프1(신규획득) 가속용 자기 블로그 마케팅, 콘텐츠 생성 검증 완료
- **노무체크AI(사장님 개인 사업)를 4번째 클라이언트로 등록** (`clients/laborcheck-ai.json`), 이후 **사업계획서(PDF) 확인으로 정정** — 처음엔 "평생교육사 기반 노무 교육 프로그램"으로 잘못 등록했으나, 실제 사업계획서 확인 결과 노무체크AI는 **AI(RAG) 기반 노무상담 플랫폼**(무료 계산기→유료 AI상담 구독 프리미엄 구조, 현재 일부 기능 운영 중)이고, 평생교육사/교육 관련 사실은 **K-eduon**이라는 별개 사업 얘기였음. `known_facts`를 사업계획서 기준으로 재작성, 잘못된 사실로 이미 생성됐던 블로그 초안(outbox, 미커밋) 삭제. K-eduon은 사장님 답변에 따라 등록 보류(나중에)
  - `labor_firm` 버티컬로 재분류 확인 완료, 클라이언트 개별 banned_terms(교육 프로그램 표현·과장 표현 금지)가 버티컬 기본 banned_terms와 정상 병합되는 것도 확인
- **사장님 실제 깃허브 저장소 2곳을 직접 열어 확인** (`aigoid-blog-bot`, `laborcheck-ai`) — 사업계획서 PDF보다 실제 코드가 훨씬 더 진행돼 있었음을 확인:
  - **노무체크AI 재차 정정**: 실제로는 RAG 상담챗봇 수준이 아니라 **회사·직원·급여명세서(카카오 발송)·근태관리·AI 근로계약서 분석까지 갖춘 B2B 멀티테넌트 SaaS**(Supabase RLS, AES-256 암호화, 로컬/클라우드 AI 엔진 선택 가능). `known_facts` 재정정 완료(커밋 `c729d50`). laborcheckai.co.kr 블로그용 **자체 콘텐츠 자동발행 시스템도 이미 있었음**(`auto_scheduled_publisher.py` + 정교한 anti-hallucination 시스템 프롬프트 — 매출엔진의 known_facts/banned_terms 원칙과 사실상 동일한 방향)
  - **주식(aigoid-blog-bot)**: 프리마켓/데일리클로즈/주간리캡 사이클로 블로그+인스타카드뉴스+유튜브쇼츠+트위터+텔레그램까지 실제로 매일 자동 발행 중인 걸 확인(오늘자 파일까지 있음). 콘텐츠 퀄리티 좋음, 과거 픽 적중률 공개 페이지도 있음
  - **⚠️ 중요 컴플라이언스 플래그 (미해결)**: 주식 카드뉴스가 특정 종목 진입가·손절가 + "지금 팔지 마라" 식 주관적 매매조언을 명시적으로 생성하도록 프롬프트돼 있음 — **유료 구독 전환 전 유사투자자문업(자본시장법) 신고 대상 여부 확인 필요**. 정확한 법 적용은 미확인, 사장님 실제 확인 필요
  - **보안 이슈 발견(미조치)**: `aigoid-blog-bot`의 `laborcheck_ai_master_pipeline.py`에 워드프레스 비밀번호·네이버 API 시크릿이 코드에 평문으로 하드코딩돼 있음(private repo라 외부유출은 아니나 로테이션 권장). `laborcheck-ai` 저장소는 스캔 결과 깨끗함(더미 플레이스홀더만 있음)
- **주식 SEO 롱테일 키워드 기능 구현** — `aigoid-blog-bot`에 `add-longtail-keyword-seo` 브랜치로 `longtail_keywords.py` + `longtail.yml` 워크플로 추가. 기존 헤드 키워드(삼성전자·코스피 등, 경쟁 심함) 대신 "삼성전자 목표주가", "8월 26일 코스피 전망" 같은 롱테일 쿼리로 검색 1위 현실적으로 노림. **master에 안 올리고 별도 브랜치 + workflow_dispatch(수동)로만 뒀음** — 기존 자동 스케줄(trending.yml)에 영향 안 주려고, 사장님 검증 후 머지 여부 결정
- **주식 블로그 "색인 4개" 원인 진단 완료 + 해결 코드 작성**: 로컬 백업(`scratch/all_posts_dump.json`)으로 실제 174개 글이 발행돼 있는 걸 확인, `utils/seo_optimizer.py`의 `ping_search_engines()`가 예전 구글/빙 핑 엔드포인트 폐지로 이미 아무것도 안 하는 no-op이었던 걸 코드 주석에서 발견(이전 작업자가 정직하게 남긴 기록). blogspot.com 서브도메인이라 IndexNow도 못 씀. → `aigoid-blog-bot`에 `add-search-console-sync` 브랜치로 `utils/search_console_sync.py`(Search Console API로 사이트맵 재제출 + 색인 상태 실측 점검, Google의 제한적 Indexing API는 정책 범위 밖이라 안 씀) + `search_console_sync.yml` 워크플로 추가. **서비스 계정 발급·서치콘솔 권한 부여는 사장님이 직접 해야 함**(코드 안 주석에 단계별 안내 포함)

**AI GROWTH OS 아키텍처 갭 채움**
- 사장님이 그린 두 다이어그램(클라이언트 데이터 모델 ①~⑦, 시스템 루프 AI GROWTH OS) 기준으로 빠진 부분 확인 → 70%는 이미 구현돼 있었고, 진짜 빠진 건 "경쟁분석 Agent"와 "AI 재전략 수립" 두 가지였음
- **`competitor_agent.py` 신규 추가** — 경쟁사를 지어내지 않는 설계(웹검색 연동이 없어서 LLM이 물으면 환각 위험 있음). `known_competitors`를 사장님이 직접 입력해야 동작, 비어있으면 분석 거부 + 이유 명시
- **`master_ai.propose_next_action()` 추가** — 병목 진단에서 한 단계 더 나아가 병목 단계별 구체적 액션 후보(`ACTIONS_BY_STAGE` 룩업) 제시, 여전히 사람 승인 필요(레벨 2 게이트 유지)
- 테스트 7개 추가, 63개 전체 통과
- **`propose_next_action()`을 `orchestrator.py`에 실제로 연결함** (`--metrics-json` 단계), 기존보다 구체적인 액션 후보가 나옴 — 새 데이터 필요 없어서 바로 적용. `competitor_agent.py`는 아직 안 물림(모든 클라이언트가 known_competitors 비어있어서 지금 넣으면 죽은 단계) — 서초김치찌개 등 실제 경쟁사 정보 채워지면 연결 예정

**사장님의 기존 자산 파악 (신규 확인, 아직 이 시스템에 미등록)**
- `www.aistoag.com` / `aigoid.blogspot.com` — 주식 콘텐츠, **이미 완전 자동화 운영 중** (블로그 + 인스타그램 릴스 + 카드뉴스 + 유튜브까지). 어떤 도구/방식으로 자동화했는지는 아직 파악 안 됨. 네트워크 정책상 이 세션에서 직접 사이트 열람 불가(`EGRESS_BLOCKED`) — 사장님 설명으로만 확인
- `노무체크ai.com` / `laborcheckai.co.kr` — 사장님 개인 사이트, 위 4번째 클라이언트(`laborcheck-ai`)로 등록한 사업과 동일

### 🔄 진행중

- **주식 블로그 커스텀 도메인 연결** — 가비아에 `blog` CNAME(`ghs.google.com.`) 등록 완료, Blogger 맞춤 도메인 `blog.aistoag.com`으로 설정 + 도메인 리디렉션 켬. **실제로 접속되는 것 확인 완료**(정상 콘텐츠 로드), 다만 HTTPS 인증서는 아직 발급 중("주의 요함" 경고 뜸) — 완료되면 코드 쪽(`utils/search_console_sync.py` 등) 도메인 주소 갱신 필요
  - **⛔ 막힘**: 네이버 서치어드바이저 소유확인(HTML 태그 방식)을 위해 Blogger 테마 HTML에 메타태그 삽입 시도 → **Blogger 자체 버그로 저장 실패**("AdSense1 위젯이 유효하지 않음" 내부 오류가 테마 저장을 막음). 위젯 삭제도 같은 에러로 실패. Blogger API는 테마/위젯 편집 기능 자체가 없어 코드로 우회 불가 — 사장님이 직접 웹 화면에서 나중에(다른 기기·시간에) 재시도 필요
  - 내일 자동화 자체는 문제없음 확인 완료 — Blogger 발행 API는 BLOG_ID 기반이라 도메인/테마 상태와 무관하게 정상 작동
  - **구글 서치콘솔에서 `aistoag.com`은 이미 도메인 전체(sc-domain:) 속성으로 확인돼 있었음** — `blog.aistoag.com`도 그 하위 도메인이라 별도 인증 없이 자동 포함될 가능성 높음. `aigoid.blogspot.com`은 도메인 이전하면서 "확인 안됨"으로 넘어감(리디렉션 켜놨으니 문제 없음)
  - **`aistoag.com`(웹, aigoid-insight-web) 서치콘솔 색인 현황도 확인**: 12개 중 5개 색인/7개 미색인이지만, 미색인 사유(로그인필요 페이지, 중복 로그인URL, 리디렉션)가 다 정상적인 것들이라 문제 없음 — 재요청 불필요
  - **도메인 참조 코드 업데이트 완료**(`update-custom-domain-refs` 브랜치, 아직 미머지): About/면책 페이지 링크, 사이트맵 핑 기본값, search_console_collector.py, 발행 URL 폴백 2곳 → 전부 `blog.aistoag.com`으로
  - **서치콘솔 서비스 계정 재사용 가능 발견**: `collectors/search_console_collector.py`에 이미 서비스 계정(`search-console-reader@aigoid-blog-automation-500804.iam.gserviceaccount.com`)이 블로그+aistoag.com 양쪽에 "전체" 권한으로 등록돼 있음. `search_console_sync.py`(add-search-console-sync 브랜치)를 이 계정과 같은 시크릿 이름(`GOOGLE_SEARCH_CONSOLE_CREDENTIALS_JSON`)을 쓰도록 맞춤 — **GitHub Secrets에 이미 등록돼 있으면 새 서비스 계정 안 만들어도 됨**, 없으면 새로 등록
  - **노무체크AI 리디렉션 무한루프 버그 발견+수정**: `laborcheckai.co.kr`(Vercel) 서치콘솔에서 142개 페이지 "리디렉션 실패" 확인 → `vercel.json`의 `/(.*) → 노무체크ai.com` 리디렉션에 호스트 조건이 없어서, `노무체크ai.com` 자신도 이 규칙에 걸려 자기 자신으로 리디렉션(무한루프)되고 있었음(사장님이 직접 `노무체크ai.com` 접속 시 주소창이 `laborcheck-ai.vercel.app`로 바뀌는 것으로 확인). `laborcheck-ai` 저장소 `fix-vercel-redirect-loop` 브랜치에 호스트 조건(`has: host`) 추가해서 수정, 푸시 완료(미머지)
- **서초김치찌개 브리프** — 상호명·지역·업종 확정, 전화번호·정확한 키워드는 미확정
- **API 키 정식 등록** — 테스트용 키로 1회 작동 확인만 됨, GitHub Secrets 정식 등록 전
- **서초김치찌개 사례 만들기(루프1 재료)** — 목표: 한 달 안에 신규고객 증가를 사례로 만들어 다음 유료고객 세일즈에 쓴다. 베이스라인 기록 시작(`performance_log.jsonl`):
  - 월매출: **5,500만~5,600만원 (사장님 추정치, 정확한 장부 수치 아님)** — 발행 전 베이스라인, 기록 완료
  - 리뷰 개수·하루 평균 손님 수: 아직 미확인
  - 발행이 시작돼야 "한 달" 카운트다운이 시작됨 — 네이버 계정·전화번호가 관건

### 📋 할 것 (다음 순서, 막힌 것 풀리는 대로)

- 서초김치찌개 실제 발행 (네이버 계정 필요)
- 노무사무실 브리프 수집 → 콘텐츠 생성
- 카카오 알림톡 대행사 계약(리뷰·리텐션 기능 활성화용)
- Phase 1 유료 전환 준비 (파일럿 사례 나오면)
- K-eduon 클라이언트 등록 — 사장님이 "나중에"로 미룸, 요청 시 진행
- **애드센스 승인 준비 상품화** — 구글 공식 정책(support.google.com answer/48182, 9724) + 실제 승인 사례 조사 → `adsense_readiness_agent.py`(체크리스트 점검, ads.txt 생성 — 인증기관ID `f08c47fec0942fa0`은 laborcheck-ai 실제 버그 수정 이력으로 재확인), `adsense_essential_pages.py`(소개/개인정보처리방침/연락처 페이지 생성, known_facts만 사용). **"승인 보장"은 절대 팔면 안 됨**(구글이 직접 심사, 자동화 불가 — 검색 1위 보장과 같은 이유) — "승인 확률 높이는 준비·점검"까지만 상품화. 테스트 9개 추가, 72개 전체 통과
- **실제 블로그 2곳에 애드센스 체크리스트 적용(감사+수정)**:
  - **주식 블로그(aigoid-blog-bot)**: 개인정보처리방침 페이지가 아예 없었음("투자 면책고지"는 목적이 달라 대체 안 됨) → `content/static_pages.py`에 `privacy_policy_page_html()` 추가(쿠키·AdSense·GA4 고지 포함) + `scripts/publish_static_pages.py`에 연결(`add-privacy-policy-page` 브랜치, 미머지). ads.txt/robots.txt는 Blogger API에 아예 없는 기능이라 코드로 못 고침 — **사장님이 Blogger 설정 > 크롤러 및 색인생성에서 직접 확인 필요**
  - **노무체크AI(laborcheck-ai)**: ads.txt/robots.txt는 이미 정상(퍼블리셔ID+인증기관ID `f08c47fec0942fa0` 정확, Googlebot·Mediapartners-Google 허용됨). Privacy Policy는 있었지만 광고 쿠키/구글 광고설정 옵트아웃 고지가 없어서 7번 섹션 추가. **소개(About) 페이지가 아예 없어서** 신규 생성(`About.jsx`) + 라우팅·푸터 연결 (`add-about-page-and-adsense-privacy-clause` 브랜치, 미머지)
  - 둘 다 검증된 사실(known_facts)만 사용, 지어낸 내용 없음
- **애드센스 진단을 "매뉴얼 체크리스트"에서 "실제 HTTP 진단"으로 업그레이드** — 사장님이 "대충 하지 말고 확실히" 지적 → 기존 건 사람이 True/False 입력해야 했던 틀뿐이었음을 인정하고 재작업. `check_https/check_ads_txt/check_robots_txt/check_sitemap/check_essential_pages` + `run_full_diagnostic()` 추가(전부 `requests` 기반 실제 조회). **이 세션 자체는 보안 정책상 임의 외부 도메인 직접 요청이 막혀 있어서(`curl $HTTPS_PROXY/__agentproxy/status`로 "policy denial" 직접 확인) 저는 라이브 테스트를 못 함** — 대신 `.github/workflows/adsense_diagnostic.yml`(workflow_dispatch, domain+publisher_id 입력) 추가해서 실제 인터넷 되는 GitHub Actions에서 버튼 하나로 실행 가능하게 만듦. 테스트는 HTTP 응답 모킹으로 16개 추가(ads.txt 인증기관ID 오타 재현 회귀테스트 포함), 84개 전체 통과
  - **사장님이 실행하실 것**: 이 브랜치가 main에 머지돼야 Actions 탭에서 실제로 클릭 가능(workflow_dispatch는 기본 브랜치에 있어야 함, PR #1 때 배운 것과 동일한 이유)
- **클라이언트 스키마 확장** (사장님 다이어그램 ③④⑤⑥⑦: 목표/KPI, 상품, 고객 페르소나, 채널별 광고비·성과) — 아직 `clients/*.json` 구조에 반영 안 됨, 다음 세션 후보

### ❓ 미정 (아직 결정 안 됨)

- **주식 자동화 자산(aistoag.com/aigoid.blogspot.com, 저장소 `aigoid-blog-bot`)을 이 시스템에 등록할지 여부** — 이미 별도 저장소로 완전 자동화(블로그+릴스+카드뉴스+유튜브+텔레그램) 운영 중임을 코드로 직접 확인. 지금 매출엔진 파이프라인(영상 제작 미지원)에 편입할 실익이 있는지 확인 필요
- **유사투자자문업 신고 필요 여부** — 위 컴플라이언스 플래그 참고. 유료 구독 전환 전 사장님이 실제로 확인해야 함
- **aigoid-blog-bot의 하드코딩된 워드프레스/네이버 시크릿 로테이션 시점** — 발견만 해두고 아직 손 안 댐, 사장님 지시 대기
- **주식 PREMIUM 유료화(토스페이먼츠 연동) 착수 시점** — `aigoid-insight-web`(aistoag.com 프론트, 별도 저장소) 확인 결과 구독 등급 로직(subscriptions 테이블, tier 체크, 관리자 수동 토글)은 이미 완성, 결제만 "빌드 순서 9단계 — 토스페이먼츠 테스트 연동" 대기 중. 사장님이 "지금은 파악만, 구현은 나중에"로 확인 — 실제 착수는 지시 있을 때

- 저장소 이름/About 설명 변경 시점 — 사장님이 직접 하기로 함, 시점 미정
- 4단계 실제 웹 대시보드(Vercel+Supabase) 착수 시점 — 고객 6곳+ 트리거 대기
- 5단계 SaaS 실제 인프라 착수 시점
- 6단계 신규 업종(병원일반/미용실/학원/법무법인) 실제 착수 시점 — 법조문 검증 필요
- 치과 Phase 3 착수 시점
- **네이버 블로그(원클릭 승인형 유지) vs 워드프레스 전환(완전자동, SEO 새로 쌓아야 함)** — 트레이드오프 설명함, 아직 결정 안 됨. 결정 전까지 워드프레스 연동 코드는 안 만듦

### 👤 내가할거 (사장님 액션 — 코드로 못 하는 것)

- [ ] `ANTHROPIC_API_KEY` 신규 발급 + GitHub Secrets 등록 (기존 테스트 키는 채팅 노출로 교체 권장)
- [ ] 서초김치찌개 전화번호 확인
- [ ] 노무사무실 브리프 작성(`docs/onboarding-brief-form.md` 사용)
- [ ] 네이버 블로그 + 스마트플레이스 계정 개설 (2곳)
- [ ] (선택) 저장소 이름/About 설명 변경

---

## 세션 로그

### 2026-08-25
위 현황판 전체가 이 세션에서 만들어짐 — 마케팅 대행 전략 수립부터 코드 구현·테스트·CI/CD·실제 LLM 검증까지 1일차 전체 작업.

노무체크AI를 4번째 클라이언트로 등록. 사장님이 주식 콘텐츠(aistoag.com/aigoid.blogspot.com)가 릴스·카드뉴스·유튜브까지 이미 완전 자동화되어 있다고 밝힘 — 어떤 도구인지, 이 시스템에 편입할지는 다음 확인 필요.

사장님이 노무체크AI 사업계획서(PDF) 공유 → 첫 등록 내용이 틀렸던 것 발견(교육 프로그램이 아니라 AI 노무상담 플랫폼, 교육 얘기는 별개 사업 K-eduon). known_facts 정정, 잘못된 사실로 생성됐던 초안 삭제. K-eduon 등록은 사장님이 나중으로 미룸.

사장님이 "다 깃허브에 있다"고 알려줘서 실제 저장소(`aigoid-blog-bot`, `laborcheck-ai`)를 직접 열어 확인. 노무체크AI는 사업계획서보다 훨씬 진행된 B2B SaaS(급여·근태·AI계약서분석)였음을 재확인해 known_facts 재정정. 주식 자동화는 실제로 매일 돌고 있는 걸 코드로 확인했고, 유사투자자문업 컴플라이언스 이슈(진입가·손절가 포함 매매조언)와 워드프레스/네이버 시크릿 하드코딩 이슈를 발견해 플래그만 해두고 진행(융통성 있게 하기로 합의 — 법적 이슈는 짧게 플래그만 남기고 작업 계속).
