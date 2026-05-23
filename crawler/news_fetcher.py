import feedparser
import requests
from datetime import datetime, timezone
from typing import Any

RSS_FEEDS = [
    # 반도체/AI 영문 뉴스
    {"source": "Reuters Tech", "url": "https://feeds.reuters.com/reuters/technologyNews"},
    {"source": "The Verge AI", "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"},
    # 국내 뉴스 (네이버 금융 반도체 검색 RSS)
    {"source": "Naver 반도체", "url": "https://news.naver.com/rss/search.nhn?query=%EB%B0%98%EB%8F%84%EC%B2%B4"},
]

KEYWORDS = ["반도체", "HBM", "NVIDIA", "AI", "GPU", "TSMC", "SK하이닉스", "삼성전자", "데이터센터", "EUV"]


def fetch_articles(max_per_feed: int = 10) -> list[dict[str, Any]]:
    articles = []
    for feed_info in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:max_per_feed]:
                title = entry.get("title", "")
                if not _is_relevant(title):
                    continue
                articles.append({
                    "title": title,
                    "source": feed_info["source"],
                    "url": entry.get("link", ""),
                    "published_at": _parse_date(entry),
                })
        except Exception as e:
            print(f"[크롤러] {feed_info['source']} 오류: {e}")
    return articles


def _is_relevant(title: str) -> bool:
    return any(kw.lower() in title.lower() for kw in KEYWORDS)


def _parse_date(entry) -> str:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        return dt.isoformat()
    return datetime.now(timezone.utc).isoformat()
