# GitHub Trending AI 日報系統｜使用手冊

> 最後更新：2026-08-27  
> 網站：https://k61513-wes.github.io/GithubTrending  
> Repo：https://github.com/k61513-Wes/GithubTrending

本手冊以目前 `main` 的 `.github/workflows/daily.yml`、`config.json` 與 `scripts/` 為操作現況。若手冊與 runtime 不一致，先把差異視為 documentation / implementation drift，不要直接用較舊文字覆蓋目前程式。

---

## 1. 系統簡介

GithubTrending 是一套由 GitHub Actions 自動執行的 GitHub Trending 日報系統，目前每天 **11:00（Asia/Taipei）**執行一次：

- 抓取 GitHub Trending 當日熱門專案。
- 使用 `config.json` 中啟用的 LLM 產生繁體中文摘要。
- 將結果寫入 `data/news.json`、`data/index.json` 與 `data/archive/`。
- 依設定透過 Telegram Bot 推播。
- 由 GitHub Actions 將更新後的 `data/` commit / push 回 repo，供 GitHub Pages 顯示最新與歷史日報。

目前 production workflow 的主要 LLM provider 是 **Groq**，第一順位模型為：

```text
groq/llama-3.3-70b-versatile
```

> 注意：repo 仍保留 `scripts/filter.py` 與 `config.json.ai_keywords`，但目前 `scripts/run_all.py` **沒有呼叫 `filter.py`**。因此現行每日主流程是「抓取 Trending → 對抓到的項目產生摘要」，`ai_keywords` 目前不會改變每日輸出內容。若未來要恢復 AI-only 篩選，應以正式程式修改接回主流程，而不是只改手冊。

---

## 2. 現行運作流程

```text
每天 11:00（Asia/Taipei）
        |
        v
GitHub Actions: .github/workflows/daily.yml
        |
        v
python scripts/run_all.py
        |
        +--> [1/4] crawler.py：抓取 GitHub Trending
        +--> [2/4] summarize.py：依 config.json 呼叫 LLM 產生繁中摘要
        +--> [3/4] 寫入 news.json / archive / index.json
        +--> [4/4] notify.py：依設定推送 Telegram
        |
        v
github-actions[bot] commit / push data/
        |
        v
GitHub Pages 顯示最新與歷史日報
```

目前 workflow cron：

```text
0 3 * * *
```

也就是 UTC 03:00 = 台灣時間 11:00。Workflow 同時支援 `workflow_dispatch` 手動觸發。

---

## 3. Repo 結構

```text
GithubTrending/
├── .github/workflows/
│   `-- daily.yml              # 排程、Python 版本、Secrets、bot push
├── scripts/
│   ├── crawler.py             # 抓 GitHub Trending
│   ├── summarize.py           # LLM 摘要；Groq / optional Gemini path
│   ├── notify.py              # Telegram 推播
│   ├── run_all.py             # 現行每日主流程
│   `-- filter.py              # AI keyword helper，目前未接入 run_all.py
├── data/
│   ├── news.json              # 最新一期
│   ├── index.json             # 歷史日期索引
│   `-- archive/               # 每日歷史 JSON
├── config.json                # LLM、通知、AI keyword 設定
├── index.html                 # GitHub Pages UI
├── app.js
├── style.css
├── requirements.txt
├── README.md                  # GitHub 首頁快速入口
├── MANUAL.md                  # 本手冊
`-- AGENTS.md                  # 專案規則
```

本 repo 目前**沒有提交 `.env.example`**。本機測試需要 `.env` 時請自行建立，不要把實際 API key / Telegram token commit 進 Git。

---

## 4. 日常設定

### 4.1 `config.json`：LLM 與通知

目前設定：

```json
{
  "notifications": {
    "telegram": true
  },
  "llm_models": [
    "groq/llama-3.3-70b-versatile",
    "//gemma-4-26b-a4b-it",
    "//gemma-4-31b-it"
  ]
}
```

模型規則：

- `//` 前綴：停用，程式會跳過。
- 沒有 `//`：啟用，依陣列順序嘗試。
- `groq/<model>`：由 `scripts/summarize.py` 呼叫 Groq OpenAI-compatible endpoint。
- 非 `groq/` 的 model name：走程式保留的 Gemini API path，且必須另外提供 `GEMINI_API_KEY`。
- 至少必須有一個啟用模型。

目前正式 GitHub Actions 只注入 `GROQ_API_KEY`，因此 production 設定應以 Groq active model 為準。

### 4.2 `ai_keywords`：目前不是 production filter

`config.json` 仍保留：

```json
"ai_keywords": {
  "模型名稱": [...],
  "技術術語": [...],
  "應用場景": [...],
  "通用詞": [...]
}
```

這些 keyword 會被 `scripts/filter.py` 讀取，但**現行 `run_all.py` 沒有呼叫 `filter_ai()`**。因此：

- 編輯 `ai_keywords` 目前不會改變每日 GitHub Actions 日報內容。
- 不要把「keyword 已存在」誤認為「production 已啟用篩選」。
- 若要恢復過濾功能，需要修改主流程並驗證輸出 schema / Pages / Telegram 是否仍一致。

### 4.3 GitHub Secrets

目前 `.github/workflows/daily.yml` 需要：

| Secret | 用途 |
| --- | --- |
| `GROQ_API_KEY` | 現行 LLM 摘要 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot |
| `TELEGRAM_CHAT_ID` | Telegram 推播目的地 |

Secret 更換後，下次 workflow 執行即使用新值，不需要修改 repo 內檔案。

---

## 5. 本機執行

### 5.1 建立 Python 環境

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell 可改用：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 5.2 建立 `.env`

目前 production Groq 設定最少需要：

```text
GROQ_API_KEY=你的_groq_api_key
TELEGRAM_BOT_TOKEN=你的_bot_token
TELEGRAM_CHAT_ID=你的_chat_id
```

如果你自行在 `config.json` 啟用了非 `groq/` model，才需要另外加入：

```text
GEMINI_API_KEY=你的_gemini_api_key
```

### 5.3 執行完整流程

```bash
python scripts/run_all.py
```

目前 console 流程是 4 段：

```text
[1/4] 抓取 GitHub Trending...
[2/4] 生成繁體中文摘要...
[3/4] 輸出 JSON 資料檔...
[4/4] 推播通知...
```

**這不是唯讀測試。** `run_all.py` 會：

- 對 GitHub Trending 發外部網路請求。
- 呼叫 Groq / 其他已啟用 LLM provider。
- 改寫 `data/news.json`、`data/index.json` 與 `data/archive/`。
- `notifications.telegram=true` 時真的發 Telegram。

只做 code review、文件檢查或 source-level verification 時，不要把 `run_all.py` 當成無副作用 smoke test。

### 5.4 只重跑 Telegram 推播

這個操作也會真的發訊息：

```bash
python -c "
import json, sys
sys.path.insert(0, 'scripts')
from notify import notify
with open('data/news.json', encoding='utf-8') as f:
    d = json.load(f)
notify(d['date'], d['projects'])
"
```

---

## 6. GitHub Actions 自動排程

### 排程

| 設定 | 現況 |
| --- | --- |
| Cron | `0 3 * * *` |
| UTC | 03:00 |
| Asia/Taipei | 11:00 |
| Python | 3.11 |
| Trigger | schedule + `workflow_dispatch` |

### 手動觸發

1. 打開 repo 的 **Actions**。
2. 選擇 `Daily AI News`。
3. 點 `Run workflow`。
4. 確認後執行。

手動 dispatch 會真的抓資料、呼叫 LLM、寫入 `data/`、可能發 Telegram，並由 workflow push 更新結果。

### 成功後應看到

- GitHub Actions run 成功。
- `data/news.json` 的 `date` / `generated_at` 更新。
- `data/archive/YYYY-MM-DD.json` 存在當日資料。
- `data/index.json` 包含當日日期。
- Telegram 啟用時收到推播。
- 若 `data/` 有變更，repo 出現 `github-actions[bot]` 的 daily commit。

Commit message 格式：

```text
chore: update daily AI news YYYY-MM-DD
```

---

## 7. Telegram 推播

`notify.py` 目前使用 Telegram Bot API `sendMessage`，格式為 HTML parse mode。

推播順序：

1. 日期 + 今日專案數量。
2. 每個專案一則：名稱、今日 stars、language、繁中摘要、GitHub URL。
3. 最後一則 GitHub Pages 網站連結。

每則訊息之間等待 0.5 秒。單則訊息若超過 Telegram 4096 字元限制會被截斷。

網站連結：

```text
https://k61513-wes.github.io/GithubTrending
```

---

## 8. GitHub Pages

靜態前端直接讀 repo 內 JSON，不需要 Web backend：

| 資料 | 檔案 |
| --- | --- |
| 最新日報 | `data/news.json` |
| 歷史日期 | `data/index.json` |
| 歷史日報 | `data/archive/YYYY-MM-DD.json` |

主要前端檔案：

```text
index.html
app.js
style.css
```

如果 workflow 成功但網站看起來沒有更新，先確認 `data/` 是否真的有新的 commit，再檢查 GitHub Pages deployment / browser cache。

---

## 9. 金鑰管理

### Groq

目前 production workflow 使用 `GROQ_API_KEY`。請在 Groq 帳號端建立 API key，放入 GitHub Actions Secret 或本機 `.env`；不要寫進 `config.json`、README、MANUAL、log 或 commit。

### Telegram Bot Token

1. 在 Telegram 找 `@BotFather`。
2. 用 `/newbot` 建立 Bot。
3. 將 token 放入 `TELEGRAM_BOT_TOKEN`。

### Telegram Chat ID

1. 先傳一則訊息給 Bot。
2. 透過 Telegram Bot API `getUpdates` 查詢 chat id。
3. 將 id 放入 `TELEGRAM_CHAT_ID`。

### Optional Gemini path

程式碼仍支援非 `groq/` model 走 Gemini API，但目前 GitHub Actions 沒有注入 `GEMINI_API_KEY`。只有在你明確重新啟用 Gemini model 並同步 workflow / Secret 時才使用。

---

## 10. 常見問題

### GitHub Actions 顯示 `GROQ_API_KEY 未設定`

- 確認 `config.json` 有啟用 `groq/` model。
- 到 GitHub Actions Secrets 確認 `GROQ_API_KEY` 存在且有效。

### LLM 出現 429 / 500 / 503

`summarize.py` 會將該 model 視為失敗並嘗試下一個啟用 model。若只有一個 active model，最後可能留下空摘要。檢查 provider quota / status 與 `config.json` active model 設定。

### Telegram 收不到

- 確認 `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`。
- 確認 `notifications.telegram` 沒有設為 `false`。
- 確認 workflow log 中 notify 階段沒有 Telegram error。

### 日報內容不是只有 AI 專案

這是目前 runtime 的已知行為：`run_all.py` 沒有接入 `filter.py`。`ai_keywords` 目前只是未接入主流程的 helper config。若要改回 AI-only，需要正式修改 pipeline，不能只調 keyword。

### 網站沒有更新

1. 確認 workflow 是否成功。
2. 確認 `data/news.json` 是否已有新 commit。
3. 確認 GitHub Pages deployment。
4. 再處理瀏覽器 cache。

### `exit code 128` / push 失敗

目前 workflow 需要 `permissions: contents: write` 才能由 `github-actions[bot]` push `data/`。

---

## 11. 使用量與成本

本專案依賴 GitHub Actions、Groq、Telegram 與 GitHub Pages。實際免費額度、速率限制與費用會隨各服務方案調整，因此本手冊**不把 `$0`、固定 requests/day 或固定 Actions 分鐘數當成長期契約**。

需要判斷當下成本或 quota 時，請以各服務帳號當下方案與官方 dashboard 為準。

---

## 12. 文件與現行正本

| 類型 | 目前來源 |
| --- | --- |
| Agent / 開發規則 | `AGENTS.md` |
| 排程、Python、Secrets | `.github/workflows/daily.yml` |
| LLM / notification / keywords 設定 | `config.json` |
| 真正每日 pipeline | `scripts/run_all.py` + `scripts/` |
| 使用手冊 | `MANUAL.md` |
| GitHub 專案入口 | `README.md` |
| 每日產出 evidence | `data/` + Git history |

手冊應描述目前可觀察 runtime，不應用歷史內容覆蓋程式；反過來，若某項產品需求應存在但 runtime 沒有實作，也應明確標示為 requirement / implementation drift，而不是默默把需求刪掉。
