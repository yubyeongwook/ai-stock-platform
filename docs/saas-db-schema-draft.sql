-- 5단계(멀티테넌트 SaaS 전환) 대비 스키마 초안 — 설계만 해둔 것, 실제 프로비저닝 안 함
-- docs/north-star-vision.md 7절 참고. Vercel+Supabase(Postgres) 기준으로 작성.
-- 지금 clients/*.json 구조를 그대로 테이블화한 것뿐이라, 5단계 착수 시 이 스키마를
-- 그대로 Supabase 프로젝트에 적용하면 된다 — 코드(orchestrator.py 등)를 새로 짜지 않고
-- 데이터 소스만 JSON 파일에서 이 테이블로 바꾸는 식으로 전환한다.

create table subscribers (
    id uuid primary key default gen_random_uuid(),
    email text unique not null,
    created_at timestamptz not null default now(),
    subscription_tier text not null check (subscription_tier in ('basic', 'growth', 'performance')),
    stripe_customer_id text -- 결제 연동 시 사용, 지금은 미정
);

-- clients/*.json 하나가 이 테이블 row 하나가 된다
create table businesses (
    id uuid primary key default gen_random_uuid(),
    subscriber_id uuid not null references subscribers(id) on delete cascade,
    slug text unique not null,
    business_name text not null,
    category text not null,
    location text,
    keywords text[] not null default '{}',
    review_target_phone text,
    ga4_property_id text,
    first_visit_benefit text,
    banned_terms text[] not null default '{}', -- business_dna.py가 채우는 기본값 + 구독자 추가분
    vertical text, -- business_dna.classify_business() 결과 캐시
    override_vertical_hold boolean not null default false,
    created_at timestamptz not null default now()
);

-- 구독자별 OAuth 연동 크리덴셜 — .env의 카카오/메타/GA4 값이 구독자별로 여기 들어간다
-- 실제 값은 암호화 저장 필요(Supabase Vault 등), 이건 스키마 설계일 뿐 암호화 구현 아님
create table integration_credentials (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null references businesses(id) on delete cascade,
    provider text not null check (provider in ('kakao_alimtalk', 'meta_ads', 'ga4')),
    credentials jsonb not null, -- {"api_key": "...", "sender_key": "..."} 형태, 암호화 필요
    connected_at timestamptz not null default now()
);

-- orchestrator.py의 outbox/ 파일들이 여기로 옮겨간다
create table content_outputs (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null references businesses(id) on delete cascade,
    content_type text not null check (content_type in ('blog_draft', 'place_plan')),
    body text not null,
    generated_at timestamptz not null default now(),
    status text not null default 'draft' check (status in ('draft', 'approved', 'published', 'rejected')),
    approved_by text, -- 구독자 본인 원클릭 승인 (docs/north-star-vision.md 7절 "원클릭 승인형")
    approved_at timestamptz
);

-- performance_log.py의 jsonl 로그가 여기로 옮겨간다 — master_ai.py 벤치마크 자동 갱신의 데이터 소스
create table performance_metrics (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null references businesses(id) on delete cascade,
    recorded_at timestamptz not null default now(),
    metrics jsonb not null -- {"impressions": 320, "ctr": 0.025, ...}
);

-- 인덱스: 구독자별 업체 목록 조회, 업체별 최근 산출물 조회가 가장 흔한 쿼리일 것으로 예상
create index idx_businesses_subscriber on businesses(subscriber_id);
create index idx_content_outputs_business on content_outputs(business_id, generated_at desc);
create index idx_performance_metrics_business on performance_metrics(business_id, recorded_at desc);
