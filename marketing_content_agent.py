"""일일 시장 브리핑용 마케팅 콘텐츠 초안을 생성하는 콘텐츠 에이전트.

`us_market_collector.py`가 수집한 시세/뉴스 데이터를 받아
소셜 게시물 초안과 블로그(뉴스레터) 초안을 만든다.
LLM/외부 API 없이 규칙 기반으로 동작하므로 별도 키 없이 바로 실행할 수 있다.
"""

from datetime import datetime

DISCLAIMER = "※ 본 콘텐츠는 투자 참고용 정보이며, 투자 판단 및 그 결과에 대한 책임은 본인에게 있습니다."


def _format_market_line(row: dict) -> str:
    if row.get("status") != "ok" or row.get("change_percent") is None:
        return f"- {row['name']}: 데이터 없음"

    change = row["change_percent"]
    arrow = "▲" if change >= 0 else "▼"
    return f"- {row['name']}: {row['price']} ({arrow}{abs(change)}%)"


def build_daily_briefing(market_rows: list[dict], news_rows: list[dict], date: str | None = None) -> dict:
    """market_rows/news_rows는 각각 get_market_data()/get_news()의 to_dict('records') 결과 형식."""

    date = date or datetime.now().strftime("%Y-%m-%d")

    market_lines = [_format_market_line(row) for row in market_rows]
    top_news = news_rows[:3]

    social_post = "\n".join(
        [
            f"📈 {date} 미국 시장 브리핑",
            "",
            *market_lines,
            "",
            "오늘의 헤드라인",
            *[f"· {n['title']}" for n in top_news],
            "",
            DISCLAIMER,
        ]
    )

    blog_lines = [f"# {date} 미국 시장 브리핑", "", "## 오늘의 시세", ""]
    blog_lines += market_lines
    blog_lines += ["", "## 오늘의 주요 뉴스", ""]
    for n in news_rows:
        blog_lines.append(f"- [{n['source']}] {n['title']}")
        if n.get("link"):
            blog_lines.append(f"  {n['link']}")
    blog_lines += ["", DISCLAIMER]
    blog_draft = "\n".join(blog_lines)

    return {"social_post": social_post, "blog_draft": blog_draft}


def generate_from_collector() -> dict:
    """us_market_collector.py를 호출해 실제 데이터로 브리핑을 생성한다."""

    from us_market_collector import get_market_data, get_news

    market_df = get_market_data()
    news_df = get_news()

    return build_daily_briefing(
        market_df.to_dict("records"),
        news_df.to_dict("records"),
    )


def save_briefing(briefing: dict, date: str | None = None) -> None:
    date = date or datetime.now().strftime("%Y-%m-%d")

    with open(f"daily_briefing_social_{date}.txt", "w", encoding="utf-8") as f:
        f.write(briefing["social_post"])

    with open(f"daily_briefing_blog_{date}.md", "w", encoding="utf-8") as f:
        f.write(briefing["blog_draft"])

    print(f"콘텐츠 초안 저장 완료: daily_briefing_social_{date}.txt, daily_briefing_blog_{date}.md")


def main():
    briefing = generate_from_collector()
    save_briefing(briefing)


if __name__ == "__main__":
    main()
