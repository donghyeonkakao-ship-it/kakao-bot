import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import yfinance as yf
from datetime import date
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from crawler.news_fetcher import fetch_articles
from ai.summarizer import summarize_articles
from database.supabase_client import get_client

load_dotenv()


def run_daily_briefing():
    print("[배치] 일일 브리핑 생성 시작")
    today = date.today().isoformat()
    db = get_client()

    # 1. 주가 데이터 수집
    nasdaq_summary = _get_price_summary("^IXIC", "나스닥")
    soxx_summary = _get_price_summary("SOXX", "SOXX")

    # 2. 뉴스 수집
    articles = fetch_articles(max_per_feed=10)
    print(f"[배치] 수집된 뉴스: {len(articles)}건")

    # 3. AI 요약
    news_summary = summarize_articles(articles)

    # 4. 상위 뉴스 3건 저장용
    top_news = [{"title": a["title"], "url": a["url"], "source": a["source"]}
                for a in articles[:3]]

    # 5. Supabase에 저장 (upsert)
    db.table("daily_briefings").upsert({
        "date": today,
        "nasdaq_summary": nasdaq_summary,
        "soxx_summary": soxx_summary,
        "top_news": top_news,
    }).execute()

    # 6. 개별 기사도 저장 (중복 방지: url 기준)
    for article in articles:
        existing = db.table("articles").select("id").eq("url", article["url"]).execute()
        if not existing.data:
            db.table("articles").insert({
                "title": article["title"],
                "source": article["source"],
                "url": article["url"],
                "published_at": article["published_at"],
                "summary_3line": news_summary,
            }).execute()

    print(f"[배치] 완료: {today}")


def _get_price_summary(ticker: str, name: str) -> str:
    try:
        data = yf.Ticker(ticker).history(period="2d")
        if len(data) < 2:
            return "데이터 없음"
        prev_close = data["Close"].iloc[-2]
        last_close = data["Close"].iloc[-1]
        change_pct = (last_close - prev_close) / prev_close * 100
        direction = "▲" if change_pct >= 0 else "▼"
        return f"{last_close:,.2f} ({direction}{abs(change_pct):.2f}%)"
    except Exception as e:
        print(f"[배치] {name} 주가 오류: {e}")
        return "데이터 없음"


if __name__ == "__main__":
    run_daily_briefing()
