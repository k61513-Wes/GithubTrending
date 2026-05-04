# GitHub Trending AI 日報

每天早上 09:00（台灣時間）自動抓取 GitHub Trending，過濾 AI/LLM 相關專案，生成繁體中文摘要，推送 Telegram 通知，並更新 GitHub Pages 靜態網站。

**網站：** https://k61513-wes.github.io/GithubTrending

## 環境設定

複製 `.env.example` 為 `.env`，填入金鑰：

```
cp .env.example .env
```

## 安裝相依套件

```
pip install -r requirements.txt
```

## 本地執行

```
python scripts/run_all.py
```

## GitHub Secrets 設定

前往 `Settings → Secrets and variables → Actions`，新增以下三個 Secret：

| Secret 名稱 | 說明 |
|------------|------|
| `GEMINI_API_KEY` | Gemini API 金鑰 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | 推播目標 Chat ID |
