import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SITE_URL = "https://k61513-wes.github.io/GithubTrending"
TELEGRAM_MAX_LEN = 4096


def send_message(bot_token: str, chat_id: str, text: str) -> dict:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=15)
    return resp.json()


def split_messages(text: str, max_len: int = TELEGRAM_MAX_LEN) -> list[str]:
    if len(text) <= max_len:
        return [text]
    parts = []
    while text:
        parts.append(text[:max_len])
        text = text[max_len:]
    return parts


def build_message(date: str, projects: list[dict]) -> str:
    number_emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    lines = [f"📅 <b>{date} AI 日報</b>", "", f"今日共發現 {len(projects)} 個 AI 相關專案 🔥", ""]

    for i, p in enumerate(projects):
        num = number_emojis[i] if i < len(number_emojis) else f"{i+1}."
        lines.append(f"{num} <b>{p['name']}</b> ⭐ +{p.get('stars_today', 0)}")
        if p.get("summary_zh"):
            lines.append(f"   {p['summary_zh']}")
        lines.append(f"   🔗 {p['url']}")
        lines.append("")

    lines.append(f"🌐 完整日報：{SITE_URL}")
    return "\n".join(lines)


def notify(date: str, projects: list[dict]) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise ValueError("TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID 未設定")

    try:
        message = build_message(date, projects)
        parts = split_messages(message)
        for part in parts:
            result = send_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, part)
            if not result.get("ok"):
                print(f"[WARN] Telegram 回傳錯誤：{result}")
        print(f"[OK] Telegram 推播成功，共 {len(parts)} 則訊息")
        return True
    except Exception as e:
        print(f"[ERROR] Telegram 推播失敗：{e}")
        return False


if __name__ == "__main__":
    sample_projects = [{
        "name": "ollama/ollama",
        "url": "https://github.com/ollama/ollama",
        "summary_zh": "Ollama 是讓開發者在本機執行大型語言模型的工具，支援 Llama、Gemma 等主流模型。",
        "stars_today": 523,
    }]
    notify("2026-05-04", sample_projects)
