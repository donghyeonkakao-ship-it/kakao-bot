from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from kakao.card_builder import build_briefing_card, build_text_response, build_loading_card
from database.supabase_client import get_client

app = FastAPI()


@app.post("/webhook")
async def kakao_webhook(request: Request):
    body = await request.json()
    utterance: str = body.get("userRequest", {}).get("utterance", "").strip()

    if "브리핑" in utterance or "오늘" in utterance:
        return JSONResponse(await get_daily_briefing_response())

    return JSONResponse(build_text_response(
        "안녕하세요! AISI입니다.\n\n"
        "📊 오늘의 브리핑 — '오늘 브리핑' 또는 '브리핑'이라고 입력하세요."
    ))


async def get_daily_briefing_response() -> dict:
    from datetime import date

    today = date.today().isoformat()
    db = get_client()

    result = db.table("daily_briefings").select("*").eq("date", today).maybe_single().execute()
    briefing = result.data if result else None

    if not briefing:
        return build_loading_card()

    nasdaq = briefing.get("nasdaq_summary", "데이터 없음")
    soxx = briefing.get("soxx_summary", "데이터 없음")
    top_news = briefing.get("top_news") or []

    description = f"📈 나스닥: {nasdaq}\n💾 SOXX: {soxx}"
    if top_news:
        description += f"\n\n🔥 주요 뉴스\n" + "\n".join(
            f"• {n.get('title', '')}" for n in top_news[:3]
        )

    return build_briefing_card(
        title="📊 오늘의 AI·반도체 브리핑",
        description=description,
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
