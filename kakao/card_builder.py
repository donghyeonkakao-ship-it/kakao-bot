from typing import Any

def build_briefing_card(title: str, description: str, url: str | None = None) -> dict[str, Any]:
    buttons = []
    if url:
        buttons.append({"label": "원문 보기", "action": "webLink", "webLinkUrl": url})
    buttons.append({"label": "투자 영향 보기", "action": "block", "messageText": "투자 영향 보기"})
    buttons.append({"label": "북마크 저장", "action": "block", "messageText": "북마크 저장"})

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "basicCard": {
                        "title": title,
                        "description": description,
                        "buttons": buttons,
                    }
                }
            ]
        },
    }


def build_text_response(text: str) -> dict[str, Any]:
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": text}}
            ]
        },
    }


def build_loading_card() -> dict[str, Any]:
    return build_text_response("브리핑을 준비 중입니다. 잠시 후 다시 요청해 주세요.")
