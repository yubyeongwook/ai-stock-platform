"""오케스트레이터 — 고객사 브리프 하나를 받아 라인 에이전트들을 돌리고 결과를 outbox에 쌓는다.

지금 실제로 자동인 것과 아닌 것을 그대로 반영한다:
- 콘텐츠 뼈대(제목·목차·CTA, 플레이스 체크리스트)는 100% 자동 — 크리덴셜 없이도 바로 돈다
- 블로그 본문은 ANTHROPIC_API_KEY가 있으면 실제 LLM이 채운다(레벨 2: AI 생성 + 사람 승인).
  없으면 뼈대만 출력하고 그렇게 명시한다 — 조용히 얼버무리지 않는다
- 카카오 알림톡·메타 광고·GA4 조회는 관련 환경변수(.env, .env.example 참고)가 없으면
  "설정 안 됨"을 그대로 알려주고 건너뛴다 — 계정을 발급받아 값을 채우면 그 즉시 동작한다
- 네이버 블로그 발행·스마트플레이스 수정은 공식 API가 없어 여기서 다루지 않는다.
  outbox에 쌓인 파일을 사람이 마지막에 복붙 발행한다 (docs/marketing-agent-plan.md 6절 참고)
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from blog_content_agent import build_blog_draft, render_markdown as render_blog_markdown
from business_dna import build_business_dna
from local_place_agent import build_local_marketing_plan, render_markdown as render_place_markdown


def load_client(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def generate_daily_outputs(client: dict, out_dir: str = "outbox") -> dict:
    dna = build_business_dna(client["business_name"], client["category"], client.get("banned_terms"))

    if not dna["vertical_active"] and not client.get("override_vertical_hold"):
        return {
            "blocked": (
                f"'{dna['vertical']}' 버티컬은 의도적으로 보류 중입니다 ({dna['compliance_note']}). "
                "정말 진행하려면 client json에 \"override_vertical_hold\": true를 명시적으로 추가하세요."
            )
        }

    today = datetime.now().strftime("%Y-%m-%d")
    client_dir = Path(out_dir) / client["slug"] / today
    client_dir.mkdir(parents=True, exist_ok=True)

    blog_draft = build_blog_draft(
        business_name=client["business_name"],
        category=client["category"],
        keywords=client["keywords"],
        location=client.get("location"),
        customer_stage=client.get("customer_stage", dna["default_customer_stage"]),
    )
    blog_path = client_dir / "blog_draft.md"

    client_with_dna = {**client, "banned_terms": dna["banned_terms"]}
    blog_body = write_blog_body(blog_draft, client_with_dna)
    if blog_body["status"] == "generated":
        content = f"# {blog_draft['title_candidates'][0]}\n\n{blog_body['text']}"
    else:
        content = render_blog_markdown(blog_draft) + f"\n\n> ⚠️ {blog_body['status']}"
    blog_path.write_text(content, encoding="utf-8")

    place_plan = build_local_marketing_plan(
        business_name=client["business_name"],
        category=client["category"],
        location=client.get("location", ""),
    )
    place_path = client_dir / "place_plan.md"
    place_path.write_text(
        render_place_markdown(place_plan, client["business_name"], client["category"], client.get("location", "")),
        encoding="utf-8",
    )

    return {"blog_draft": str(blog_path), "place_plan": str(place_path)}


def write_blog_body(blog_draft: dict, client: dict) -> dict:
    """가능하면 LLM으로 실제 본문을 채운다. 안 되면 이유를 그대로 보고한다."""

    from integrations.llm_writer import LLMWriterConfigError, write_full_blog_post

    try:
        text = write_full_blog_post(
            blog_draft,
            business_name=client["business_name"],
            category=client["category"],
            location=client.get("location"),
            banned_terms=client.get("banned_terms"),
            known_facts=client.get("known_facts"),
        )
        return {"status": "generated", "text": text}
    except LLMWriterConfigError as e:
        return {"status": f"LLM 미설정: {e}"}
    except Exception as e:  # noqa: BLE001 — API 키 오류·네트워크 오류 등, 뼈대 출력으로 계속 진행
        return {"status": f"LLM 호출 실패: {e}"}


def send_review_reminder(client: dict, dry_run: bool = True) -> dict:
    from integrations.kakao_alimtalk import AlimtalkConfigError, KakaoAlimtalkClient

    phone = client.get("review_target_phone")
    if not phone:
        return {"skipped": "client brief에 review_target_phone 없음"}

    try:
        kakao = KakaoAlimtalkClient()
    except AlimtalkConfigError as e:
        return {"skipped": f"카카오 알림톡 미설정: {e}"}

    return kakao.send(
        phone=phone,
        template_code="REVIEW_REQUEST",
        variables={"business_name": client["business_name"]},
        dry_run=dry_run,
    )


def fetch_weekly_performance(client: dict) -> dict:
    result = {}

    ga4_property_id = client.get("ga4_property_id")
    if ga4_property_id:
        try:
            from integrations.ga4_client import GA4ConfigError, get_weekly_summary

            result["ga4"] = get_weekly_summary(ga4_property_id)
        except GA4ConfigError as e:
            result["ga4"] = {"skipped": f"GA4 미설정: {e}"}
    else:
        result["ga4"] = {"skipped": "client brief에 ga4_property_id 없음"}

    if os.environ.get("META_ACCESS_TOKEN") and os.environ.get("META_AD_ACCOUNT_ID"):
        try:
            from integrations.meta_ads import MetaAdsClient

            result["meta"] = MetaAdsClient().get_account_insights()
        except Exception as e:  # noqa: BLE001 — 데모 단계에서는 리포트에 원인만 남기고 계속 진행
            result["meta"] = {"skipped": f"메타 광고 조회 실패: {e}"}
    else:
        result["meta"] = {"skipped": "META_ACCESS_TOKEN / META_AD_ACCOUNT_ID 미설정"}

    return result


def diagnose_client_priority(client: dict, metrics: dict) -> dict:
    """Master AI(master_ai.py)에게 이번 주기 우선순위를 물어본다. 실행은 안 하고 추천만 반환한다."""

    from master_ai import next_cycle_priority

    return next_cycle_priority(client["business_name"], metrics)


def main():
    parser = argparse.ArgumentParser(description="고객사 브리프 기반 일일 산출물 생성")
    parser.add_argument("client_json", help="clients/example-hospital.json 같은 브리프 파일 경로")
    parser.add_argument("--out", default="outbox", help="산출물 저장 경로")
    parser.add_argument("--metrics-json", help="성과 지표 JSON 파일 경로 — 있으면 Master AI 병목 진단도 함께 실행")
    args = parser.parse_args()

    client = load_client(args.client_json)

    outputs = generate_daily_outputs(client, args.out)
    if "blocked" in outputs:
        print(f"차단됨: {outputs['blocked']}")
        return

    print("생성 완료:")
    for name, path in outputs.items():
        print(f"  - {name}: {path}")

    review = send_review_reminder(client)
    print(f"리뷰 리마인더: {review}")

    perf = fetch_weekly_performance(client)
    print(f"주간 성과: {perf}")

    if args.metrics_json:
        with open(args.metrics_json, encoding="utf-8") as f:
            metrics = json.load(f)
        diagnosis = diagnose_client_priority(client, metrics)
        print(f"Master AI 진단: {diagnosis}")


if __name__ == "__main__":
    main()
