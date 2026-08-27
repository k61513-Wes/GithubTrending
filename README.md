# GitHub Trending AI 日報

一套由 GitHub Actions 自動執行的 AI / LLM 趨勢日報系統：每天抓取 GitHub Trending，篩選 AI 相關專案，用 LLM 產生繁體中文摘要，推送到 Telegram，並把當日與歷史資料發布到 GitHub Pages。

**網站：** https://k61513-wes.github.io/GithubTrending

> README 以目前 `main` 的 workflow / config / scripts 為現況依據。舊 `MANUAL.md` 仍有部分 09:00 / Gemini 等歷史描述；目前實際排程與 provider 已不同，詳見下方。

## 目前狀態

目前自動化主線：

```text
每天 11:00（Asia/Taipei）
        |
        v
GitHub Actions: .github/workflows/daily.yml
        |
        v
python scripts/run_all.py
        |
        +--> 抓取 GitHub Trending
        +--> AI 關鍵字篩選
        +--> LLM 產生繁體中文摘要
        +--> data/news.json
        +--> data/index.json
        +--> data/archive/YYYY-MM-DD.json
        +--> Telegram 推播
        `--> github-actions[bot] commit / push
                 |
                 v
             GitHub Pages
```

目前 workflow cron 為 `0 3 * * *`，也就是 **台灣時間 11:00**。Workflow 同時支援手動 `workflow_dispatch`。

目前 `config.json` 啟用的第一順位 LLM 為：

```text
groq/llama-3.3-70b-versatile
```

Gemma 項目目前以 `//` 前綴停用。Provider / model 應以現行 `config.json` 為準，不以舊手冊文字判斷。

## 核心功能

### Trending 抓取

`scripts/crawler.py` 取得 GitHub Trending 專案資料，作為每日候選來源。

### AI / LLM 篩選

`scripts/filter.py` 依 `config.json` 的 `ai_keywords` 判斷是否為 AI 相關內容。關鍵字目前分成模型名稱、技術術語、應用場景與通用詞等類別。

### 中文摘要

`scripts/summarize.py` 依 `config.json` 的 LLM model 設定呼叫 provider，產生給人閱讀的繁體中文摘要。

### Telegram 推播

完整流程會把日報發到指定 Telegram chat；Bot token / chat id 只來自 GitHub Secrets 或本機 `.env`，不寫進 repo。

### GitHub Pages 歷史日報

靜態網站使用 repo 內 JSON：

- `data/news.json`：最新一期。
- `data/index.json`：歷史日期索引。
- `data/archive/`：每日歷史資料。

前端由 `index.html`、`app.js`、`style.css` 讀取這些資料，不需要獨立 Web backend。

## 技術棧

| Layer | Technology |
| --- | --- |
| Automation | GitHub Actions |
| Runtime | Python 3.11（Actions） |
| Crawl / HTTP | requests、BeautifulSoup |
| LLM | Groq（目前 config 使用 Llama 3.3 70B） |
| Notification | Telegram Bot API |
| Data | JSON files in `data/` |
| Website | Static HTML / JavaScript / CSS、GitHub Pages |

## Repo 結構

```text
GithubTrending/
├── .github/workflows/daily.yml   # 每日排程與 GitHub Actions runtime
├── scripts/
│   ├── crawler.py                # GitHub Trending crawler
│   ├── filter.py                 # AI keyword filter
│   ├── summarize.py              # LLM 摘要
│   ├── notify.py                 # Telegram 推播
│   `-- run_all.py                # 完整流程入口
├── data/
│   ├── news.json                 # 最新日報
│   ├── index.json                # 歷史索引
│   `-- archive/                  # 每日日報歷史
├── config.json                   # LLM、通知與 AI 關鍵字設定
├── index.html                    # GitHub Pages UI
├── app.js
├── style.css
├── requirements.txt
├── MANUAL.md                     # 長版使用手冊（部分舊資訊待同步）
├── AGENTS.md                     # 專案規則
`-- README.md                     # GitHub 專案入口
```

## GitHub Actions 設定

目前 workflow 需要以下 GitHub Secrets：

| Secret | 用途 |
| --- | --- |
| `GROQ_API_KEY` | LLM 摘要 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot |
| `TELEGRAM_CHAT_ID` | 推播目的地 |

Workflow 具有 `contents: write`，因為每日產出完成後會由 `github-actions[bot]` commit / push `data/`。這是自動化本身的權限，不代表互動式 Agent 可以任意 push。

## 本機執行

安裝依賴：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

本 repo **目前沒有提交 `.env.example`**。若要在本機執行完整流程，請自行建立 `.env`，依當前 provider / notification 設定準備：

```text
GROQ_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

完整執行：

```bash
python scripts/run_all.py
```

**注意：這不是唯讀測試。** `run_all.py` 會進行外部網路請求、更新 `data/`，並可能真的發送 Telegram。只想 review 程式碼或驗證格式時，不要把它當 smoke test 直接執行。

## 如何調整每日內容

主要看 `config.json`：

- `notifications.telegram`：是否啟用 Telegram。
- `llm_models`：provider / model 順序；`//` 前綴代表停用。
- `ai_keywords`：Trending 專案的 AI 分類關鍵字。

排程時間與 Secrets 名稱則以 `.github/workflows/daily.yml` 為準。

## 驗證方式

純程式變更可先做 Python syntax / source-level 檢查；若修改資料 schema，還需確認：

```text
scripts output
  -> data/news.json / index.json / archive
  -> app.js / GitHub Pages reader
```

真正驗證 crawler、LLM、Telegram 或 workflow 會產生外部副作用，應明確區分「source check」與「實際 workflow test」。

## 文件與正本

| 角色 | 目前來源 |
| --- | --- |
| Agent / 開發規則 | `AGENTS.md` |
| 每日排程、Python 版本、Secrets | `.github/workflows/daily.yml` |
| LLM provider / model、關鍵字與通知開關 | `config.json` |
| 完整 pipeline 實作 | `scripts/` |
| 使用手冊 | `MANUAL.md`（部分 runtime 細節目前落後 main） |
| 日報產出 evidence | `data/` + Git history |
| DevFlow | `.agent/`（明確使用 `df-*` 時） |

若 README、MANUAL、workflow、config 與程式碼互相矛盾，應先列出 drift；不要用較舊的說明覆蓋目前 runtime，也不要默默把實作反寫成需求正本。
