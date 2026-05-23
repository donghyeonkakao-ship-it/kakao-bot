import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_model = None


def get_model():
    global _model
    if _model is None:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        _model = genai.GenerativeModel("gemini-1.5-flash")
    return _model


def summarize_articles(articles: list[dict]) -> str:
    if not articles:
        return "오늘 수집된 주요 뉴스가 없습니다."

    titles = "\n".join(f"- {a['title']} ({a['source']})" for a in articles[:10])

    prompt = (
        "다음은 오늘의 AI·반도체 관련 뉴스 목록입니다.\n\n"
        f"{titles}\n\n"
        "투자자 관점에서 핵심 흐름 3가지를 각각 한 줄로 요약해 주세요.\n"
        "형식: 번호 없이 줄바꿈으로 구분, 각 줄은 30자 이내."
    )

    response = get_model().generate_content(prompt)
    return response.text.strip()


def analyze_market_impact(article_title: str, relations: list[dict]) -> str:
    rel_text = "\n".join(
        f"- {r['keyword']}: {', '.join(r['related_stocks'])}"
        for r in relations
    )

    prompt = (
        f"뉴스 제목: {article_title}\n\n"
        f"참고할 종목 관계:\n{rel_text}\n\n"
        "이 뉴스가 반도체·AI 투자에 미치는 영향을 2문장으로 설명해 주세요. "
        "위 관계 DB에 없는 종목은 절대 언급하지 마세요."
    )

    response = get_model().generate_content(prompt)
    return response.text.strip()
