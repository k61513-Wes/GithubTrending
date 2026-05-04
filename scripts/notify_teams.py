import os
import time
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")
SITE_URL = "https://k61513-wes.github.io/GithubTrending"

NUMBER_EMOJIS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]


def send_teams_message(webhook_url: str, card_content: dict) -> bool:
    """直接送出 Adaptive Card 內容（不加外層 message 包裝）"""
    resp = requests.post(webhook_url, json=card_content, timeout=15)
    if resp.status_code in (200, 202):
        return True
    print(f"[WARN] Teams 回傳錯誤：{resp.status_code} {resp.text[:200]}")
    return False


def make_card(body: list, actions: list = None) -> dict:
    """建立純 Adaptive Card（Teams workflow webhook 要求的格式）"""
    card = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.2",
        "body": body
    }
    if actions:
        card["actions"] = actions
    return card


def build_header_card(date: str, total: int) -> dict:
    return make_card([
        {
            "type": "TextBlock",
            "text": f"📅 {date} GitHub Trending AI 日報",
            "weight": "Bolder",
            "size": "Large",
            "wrap": True
        },
        {
            "type": "TextBlock",
            "text": f"今日共發現 {total} 個 AI 相關專案 🔥",
            "wrap": True,
            "spacing": "Small"
        }
    ])


def build_project_card(index: int, project: dict) -> dict:
    num = NUMBER_EMOJIS[index] if index < len(NUMBER_EMOJIS) else f"{index+1}."
    name = project.get("name", "")
    url = project.get("url", "")
    language = project.get("language", "")
    stars_today = project.get("stars_today", 0)
    summary = project.get("summary_zh", "")

    body = [
        {
            "type": "TextBlock",
            "text": f"{num} **{name}**  ⭐ +{stars_today}",
            "weight": "Bolder",
            "wrap": True
        }
    ]

    if language:
        body.append({
            "type": "TextBlock",
            "text": f"🔧 {language}",
            "isSubtle": True,
            "spacing": "Small",
            "wrap": True
        })

    if summary:
        body.append({
            "type": "TextBlock",
            "text": summary,
            "wrap": True,
            "spacing": "Small"
        })

    return make_card(body, actions=[
        {
            "type": "Action.OpenUrl",
            "title": "開啟 GitHub",
            "url": url
        }
    ])


def build_footer_card() -> dict:
    return make_card(
        body=[{
            "type": "TextBlock",
            "text": "🌐 查看完整日報網站",
            "wrap": True
        }],
        actions=[{
            "type": "Action.OpenUrl",
            "title": "開啟網站",
            "url": SITE_URL
        }]
    )


def notify_teams(date: str, projects: list[dict]) -> bool:
    if not TEAMS_WEBHOOK_URL:
        print("[SKIP] TEAMS_WEBHOOK_URL 未設定，跳過 Teams 推播")
        return False

    try:
        cards = []
        cards.append(build_header_card(date, len(projects)))
        for i, project in enumerate(projects):
            cards.append(build_project_card(i, project))
        cards.append(build_footer_card())

        for card in cards:
            send_teams_message(TEAMS_WEBHOOK_URL, card)
            time.sleep(0.5)

        print(f"[OK] Teams 推播成功，共 {len(cards)} 則（標題 + {len(projects)} 專案 + 結尾）")
        return True

    except Exception as e:
        print(f"[ERROR] Teams 推播失敗：{e}")
        return False


if __name__ == "__main__":
    sample_projects = [
        {
            "name": "ollama/ollama",
            "url": "https://github.com/ollama/ollama",
            "summary_zh": "Ollama 是讓開發者在本機執行大型語言模型的工具，支援 Llama、Gemma 等主流模型。",
            "language": "Go",
            "stars_today": 523,
        }
    ]
    notify_teams("2026-05-04", sample_projects)
