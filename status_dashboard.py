"""미니 대시보드(4단계) — 정직한 버전.

`docs/marketing-agent-plan.md` 6절의 트리거(고객 6곳+)가 오기 전까지는 Vercel+Supabase로
된 진짜 웹 대시보드를 만들지 않기로 했다. 그래도 지금도 "한눈에 상태 보기"는 필요해서,
호스팅 없이 로컬에서 `clients/*.json` + `outbox/`를 읽어 정적 HTML 하나를 생성하는
스크립트로 대체한다. 새 인프라 없음, 새 계정 없음 — 지금 있는 파일만 읽는다.
"""

import json
from pathlib import Path

from business_dna import build_business_dna


def _latest_outbox_date(slug: str, out_dir: str = "outbox") -> str | None:
    client_dir = Path(out_dir) / slug
    if not client_dir.exists():
        return None
    dates = sorted((d.name for d in client_dir.iterdir() if d.is_dir()), reverse=True)
    return dates[0] if dates else None


def build_status_rows(clients_dir: str = "clients", out_dir: str = "outbox") -> list[dict]:
    rows = []
    for path in sorted(Path(clients_dir).glob("*.json")):
        with open(path, encoding="utf-8") as f:
            client = json.load(f)

        dna = build_business_dna(client["business_name"], client["category"], client.get("banned_terms"))
        rows.append(
            {
                "slug": client["slug"],
                "business_name": client["business_name"],
                "vertical": dna["vertical"],
                "vertical_active": dna["vertical_active"],
                "has_phone": bool(client.get("review_target_phone")),
                "latest_content_date": _latest_outbox_date(client["slug"], out_dir),
            }
        )
    return rows


def render_html(rows: list[dict]) -> str:
    lines = [
        "<!doctype html><html><head><meta charset='utf-8'><title>매출엔진 상태판</title>",
        "<style>body{font-family:sans-serif;padding:24px}table{border-collapse:collapse;width:100%}"
        "td,th{border:1px solid #ccc;padding:8px;text-align:left}"
        ".blocked{color:#b91c1c}.ok{color:#15803d}</style></head><body>",
        "<h1>매출엔진 상태판</h1>",
        "<table><tr><th>업체</th><th>업종</th><th>활성 여부</th><th>전화번호</th><th>최근 산출물</th></tr>",
    ]
    for r in rows:
        status_class = "ok" if r["vertical_active"] else "blocked"
        status_text = "활성" if r["vertical_active"] else "보류(Compliance 게이트 대기)"
        phone_text = "있음" if r["has_phone"] else "없음"
        content_text = r["latest_content_date"] or "아직 없음"
        lines.append(
            f"<tr><td>{r['business_name']}</td><td>{r['vertical']}</td>"
            f"<td class='{status_class}'>{status_text}</td><td>{phone_text}</td><td>{content_text}</td></tr>"
        )
    lines.append("</table></body></html>")
    return "\n".join(lines)


def main():
    rows = build_status_rows()
    html = render_html(rows)
    Path("status.html").write_text(html, encoding="utf-8")
    print(f"{len(rows)}개 고객사 상태를 status.html에 생성했습니다.")


if __name__ == "__main__":
    main()
