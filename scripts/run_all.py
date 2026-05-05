import os
import json
import shutil
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY 未設定，請檢查 .env 或 GitHub Secrets")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN 未設定，請檢查 .env 或 GitHub Secrets")
if not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_CHAT_ID 未設定，請檢查 .env 或 GitHub Secrets")

# 計算腳本目錄的上層（repo 根目錄）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
ARCHIVE_DIR = os.path.join(DATA_DIR, "archive")
CONFIG_PATH = os.path.join(ROOT_DIR, "config.json")

os.makedirs(ARCHIVE_DIR, exist_ok=True)

from crawler import fetch_trending
from summarize import summarize_projects
from notify import notify
from notify_teams import notify_teams


def load_notification_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config.get("notifications", {"telegram": True, "teams": True})


def get_taiwan_now() -> datetime:
    tz_taipei = timezone(timedelta(hours=8))
    return datetime.now(tz_taipei)


def write_news_json(projects: list[dict], now: datetime):
    date_str = now.strftime("%Y-%m-%d")
    generated_at = now.isoformat()

    news = {
        "generated_at": generated_at,
        "date": date_str,
        "total_count": len(projects),
        "projects": projects,
    }

    news_path = os.path.join(DATA_DIR, "news.json")
    with open(news_path, "w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    print(f"[OK] 寫入 {news_path}")
    return news_path, date_str, news


def write_archive(news_path: str, date_str: str) -> None:
    archive_path = os.path.join(ARCHIVE_DIR, f"{date_str}.json")
    shutil.copy2(news_path, archive_path)
    print(f"[OK] 備份至 {archive_path}")


def update_index(date_str: str) -> None:
    index_path = os.path.join(DATA_DIR, "index.json")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {"dates": []}

    dates = index.get("dates", [])
    if date_str not in dates:
        dates.insert(0, date_str)
    index["dates"] = dates

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"[OK] 更新 index.json，共 {len(dates)} 筆日期")


def main():
    now = get_taiwan_now()
    notif_config = load_notification_config()

    print(f"=== GitHub Trending 日報 ({now.strftime('%Y-%m-%d %H:%M')}) ===")

    print("\n[1/4] 抓取 GitHub Trending...")
    all_repos = fetch_trending()
    print(f"  共 {len(all_repos)} 筆")

    print("\n[2/4] 生成繁體中文摘要...")
    enriched = summarize_projects(all_repos)

    print("\n[3/4] 輸出 JSON 資料檔...")
    news_path, date_str, news = write_news_json(enriched, now)
    write_archive(news_path, date_str)
    update_index(date_str)

    print("\n[4/4] 推播通知...")

    if notif_config.get("telegram", True):
        print("  → Telegram")
        notify(date_str, enriched)
    else:
        print("  → Telegram [已停用]")

    if notif_config.get("teams", True):
        print("  → Teams")
        notify_teams(date_str, enriched)
    else:
        print("  → Teams [已停用]")

    print("\n=== 完成 ===")


if __name__ == "__main__":
    main()
