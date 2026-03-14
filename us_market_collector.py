import yfinance as yf
import feedparser
import pandas as pd
from datetime import datetime


def get_market_data():
    # 주요 미국 지수/종목
    tickers = {
        "NASDAQ_100_ETF(QQQ)": "QQQ",
        "S&P500_ETF(SPY)": "SPY",
        "Semiconductor_ETF(SMH)": "SMH",
        "NVIDIA(NVDA)": "NVDA",
        "Tesla(TSLA)": "TSLA",
        "Microsoft(MSFT)": "MSFT",
        "Apple(AAPL)": "AAPL",
        "AMD(AMD)": "AMD",
    }

    rows = []

    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")

            if hist.empty or len(hist) < 2:
                rows.append({
                    "name": name,
                    "symbol": symbol,
                    "price": None,
                    "change_percent": None,
                    "status": "no data"
                })
                continue

            latest_close = hist["Close"].iloc[-1]
            prev_close = hist["Close"].iloc[-2]
            change_percent = ((latest_close - prev_close) / prev_close) * 100

            rows.append({
                "name": name,
                "symbol": symbol,
                "price": round(float(latest_close), 2),
                "change_percent": round(float(change_percent), 2),
                "status": "ok"
            })

        except Exception as e:
            rows.append({
                "name": name,
                "symbol": symbol,
                "price": None,
                "change_percent": None,
                "status": f"error: {e}"
            })

    return pd.DataFrame(rows)


def get_news():
    rss_urls = {
        "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
        "CNBC Top News": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    }

    news_list = []

    for source, url in rss_urls.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                news_list.append({
                    "source": source,
                    "title": entry.get("title", ""),
                    "link": entry.get("link", "")
                })
        except Exception as e:
            news_list.append({
                "source": source,
                "title": f"RSS error: {e}",
                "link": ""
            })

    return pd.DataFrame(news_list)


def save_report(market_df, news_df):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    market_file = f"us_market_data_{now}.csv"
    news_file = f"us_market_news_{now}.csv"

    market_df.to_csv(market_file, index=False, encoding="utf-8-sig")
    news_df.to_csv(news_file, index=False, encoding="utf-8-sig")

    print("\n저장 완료")
    print(f"- 시장 데이터 파일: {market_file}")
    print(f"- 뉴스 데이터 파일: {news_file}")


def print_summary(market_df, news_df):
    print("\n=== 미국 시장 데이터 ===")
    print(market_df.to_string(index=False))

    print("\n=== 미국 뉴스 제목 ===")
    for i, row in news_df.head(10).iterrows():
        print(f"{i+1}. [{row['source']}] {row['title']}")
        print(f"   {row['link']}")


def main():
    print("미국시장 데이터 수집 시작...")
    market_df = get_market_data()
    news_df = get_news()

    print_summary(market_df, news_df)
    save_report(market_df, news_df)

    print("\n작업 완료")


if __name__ == "__main__":
    main()
