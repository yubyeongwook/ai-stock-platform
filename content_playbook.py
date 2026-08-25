"""콘텐츠 제작 노하우 라이브러리 — 코어 엔진의 실질적 해자.

일반적인 "AI가 글을 씁니다" 수준이 아니라, 실제 카피라이팅·전환심리학·
네이버 SEO 구조 원칙에 기반한 프레임워크를 코드 자산으로 담아둔다.
blog_content_agent.py와 integrations/llm_writer.py가 이 모듈을 참조해서
산출물의 질 자체를 경쟁사가 못 따라오게 만드는 게 목적이다
(docs/competitive-moat.md 3절 "업종 플레이북 자산화"의 실제 구현체).

여기 담긴 원칙의 근거:
- 헤드라인 공식(4U: Useful/Urgent/Unique/Ultra-specific)은 카피라이팅에서
  널리 검증된 프레임워크(Michael Masterson)
- 전환 심리학은 Cialdini의 설득의 6원칙 중 로컬 비즈니스 콘텐츠에
  실제로 적용 가능한 것만 추림
- 네이버 SEO 규칙은 네이버가 공식 발표한 C-Rank/D.I.A. 로직의 공개된 원칙
  (정확한 가중치·알고리즘은 비공개이므로 "일반적으로 알려진 방향성"으로 취급할 것)
"""

# ---------------------------------------------------------------------------
# 1. 헤드라인 공식 — 4U 원칙(Useful/Urgent/Unique/Ultra-specific)
# "강남 정형외과 좋은 곳" 같은 밋밋한 제목이 아니라 아래 공식으로 만든다.
# 필드는 blog_content_agent.py가 이미 가진 값(keyword/category/location/number)만
# 쓰도록 설계했다 — 없는 정보를 억지로 채우면 문장이 어색해지기 때문.
# ---------------------------------------------------------------------------

HEADLINE_FORMULAS = [
    {
        "name": "초구체적 니즈 타겟팅",
        "template": "{keyword}, 지금 확인해야 할 이유",
        "why": "막연한 '좋은 곳'보다 구체적 니즈를 걸면 검색자가 '내 얘기다'라고 즉시 인식해 클릭률이 오른다",
    },
    {
        "name": "숫자 기반 신뢰",
        "template": "{location}{category}, {number}가지 확인 포인트",
        "why": "숫자는 콘텐츠 구조를 예고해 완독 가능성을 높인다 — 스캔 가능성이 좋아 체류시간에 유리",
    },
    {
        "name": "질문형 공감",
        "template": "{keyword}, 이것 때문에 고민이신가요?",
        "why": "질문형은 독자의 내적 대화를 그대로 반영해 공감을 만든다 — 정보 탐색 초기 단계 고객에게 효과적",
    },
    {
        "name": "비교/선택 가이드",
        "template": "{category} 선택 전 반드시 비교해야 할 {number}가지",
        "why": "비교 단계 고객(정보탐색→선택 직전)에게 최적 — 신뢰와 체류시간을 동시에 만든다",
    },
]

_STAGE_TO_FORMULA_INDEX = {
    "awareness": 2,   # 질문형 공감 — 처음 검색하는 사람
    "comparison": 3,  # 비교/선택 가이드
    "decision": 0,    # 초구체적 니즈 타겟팅 — 방문 직전
}


def pick_headline_formula(customer_stage: str = "awareness") -> dict:
    """고객 여정 단계에 맞는 헤드라인 공식을 고른다.

    customer_stage: "awareness"(처음 검색) | "comparison"(비교) | "decision"(선택 직전)
    """
    index = _STAGE_TO_FORMULA_INDEX.get(customer_stage, 2)
    return HEADLINE_FORMULAS[index]


def render_headline(formula: dict, keyword: str, category: str, location: str | None, number: int = 3) -> str:
    location_prefix = f"{location} " if location else ""
    title = formula["template"].format(keyword=keyword, category=category, location=location_prefix, number=number)
    return " ".join(title.split())  # 빈 location 등으로 생긴 중복 공백 정리


# ---------------------------------------------------------------------------
# 2. 네이버 SEO 구조 원칙 — C-Rank/D.I.A. 로직 방향성에 기반한 실전 체크리스트
# ---------------------------------------------------------------------------

NAVER_SEO_RULES = [
    "첫 2~3문장 안에 핵심 키워드와 글의 답을 압축 제시한다 (검색결과 미리보기 노출 구간)",
    "정보 나열이 아니라 경험·사례 기반 서술을 섞는다 — D.I.A. 로직은 '직접 경험'을 고품질 신호로 본다",
    "체류시간을 늘리도록 소제목·목록으로 스캔 가능한 구조를 만든다",
    "같은 블로그는 한 업종·주제에 일관되게 발행한다 — C-Rank는 출처의 주제 일관성을 본다",
    "키워드를 억지로 반복하지 않는다 — 과도한 키워드 밀도는 저품질 판정 신호",
]

# ---------------------------------------------------------------------------
# 3. 전환 심리학 — Cialdini 설득 원칙 중 로컬 비즈니스에 실제로 먹히는 것만
# ---------------------------------------------------------------------------

CONVERSION_PRINCIPLES = [
    {"principle": "구체적 사회적 증거", "rule": "'많은 고객이'가 아니라 실제 확인 가능한 구체적 숫자·사례를 쓴다(과장·허위 금지)"},
    {"principle": "손실 회피", "rule": "'얻는 것'뿐 아니라 '지금 확인 안 하면 놓치는 것'을 사실 기반으로 한 번은 짚는다"},
    {"principle": "단일 CTA", "rule": "행동 유도는 하나만 명확하게 — 여러 CTA를 나열해 선택지를 늘리지 않는다"},
    {"principle": "리스크 역전", "rule": "가능하면 진입장벽을 낮추는 요소(무료 상담 등)를 포함한다"},
]


def build_playbook_instructions(customer_stage: str = "awareness") -> str:
    """LLM 프롬프트에 그대로 삽입 가능한 형태로 플레이북을 문자열화한다."""

    formula = pick_headline_formula(customer_stage)
    seo_lines = "\n".join(f"- {r}" for r in NAVER_SEO_RULES)
    conv_lines = "\n".join(f"- {c['principle']}: {c['rule']}" for c in CONVERSION_PRINCIPLES)

    return f"""[헤드라인 접근법 — {formula['name']}]
{formula['why']}

[네이버 SEO 구조 원칙 — 반드시 지킬 것]
{seo_lines}

[전환 심리학 원칙 — 본문·CTA에 반영할 것]
{conv_lines}
"""
