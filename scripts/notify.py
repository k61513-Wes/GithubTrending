import os
import time
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


def build_header(date: str, total: int) -> str:
    """第一則：日期標題 + 今日總數"""
    return (
        f"📅 <b>{date} AI 日報</b>\n"
        f"\n"
        f"今日共發現 {total} 個 AI 相關專案 🔥"
    )


def build_project_message(index: int, total: int, project: dict) -> str:
    """每個專案一則訊息"""
    number_emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    num = number_emojis[index] if index < len(number_emojis) else f"{index+1}."

    lines = [
        f"{num} <b>{project['name']}</b>  ⭐ +{project.get('stars_today', 0)}",
    ]
    if project.get("language"):
        lines.append(f"🔧 {project['language']}")
    if project.get("summary_zh"):
        lines.append(f"\n{project['summary_zh']}")
    lines.append(f"\n🔗 {project['url']}")

    return "\n".join(lines)


def build_footer() -> str:
    """最後一則：網站連結"""
    return f"🌐 完整日報：{SITE_URL}"


def notify(date: str, projects: list[dict]) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise ValueError("TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID 未設定")

    try:
        messages = []

        # 第一則：標題
        messages.append(build_header(date, len(projects)))

        # 每個專案各一則
        for i, project in enumerate(projects):
            msg = build_project_message(i, len(projects), project)
            # 單則超過上限時截斷（極少發生）
            if len(msg) > TELEGRAM_MAX_LEN:
                msg = msg[:TELEGRAM_MAX_LEN - 3] + "..."
            messages.append(msg)

        # 最後一則：網站連結
        messages.append(build_footer())

        # 依序發送，每則間隔 0.5 秒避免 rate limit
        for msg in messages:
            result = send_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, msg)
            if not result.get("ok"):
                print(f"[WARN] Telegram 回傳錯誤：{result}")
            time.sleep(0.5)

        print(f"[OK] Telegram 推播成功，共 {len(messages)} 則（標題 + {len(projects)} 專案 + 結尾）")
        return True

    except Exception as e:
        print(f"[ERROR] Telegram 推播失敗：{e}")
        return False


if __name__ == "__main__":
    sample_projects = [
        {
            "name": "ollama/ollama",
            "url": "https://github.com/ollama/ollama",
            "summary_zh": "Ollama 是讓開發者在本機執行大型語言模型的工具，支援 Llama、Gemma 等主流模型。",
            "language": "Go",
            "stars_today": 523,
        },
        {
            "name": "openai/whisper",
            "url": "https://github.com/openai/whisper",
            "summary_zh": "Whisper 是 OpenAI 開發的開源語音辨識模型，支援多語言轉錄與翻譯。",
            "language": "Python",
            "stars_today": 341,
        },
    ]
    notify("2026-05-04", sample_projects)
