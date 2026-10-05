# GitHub Trending 中文日報

這個專案把 GitHub Trending 的熱門專案整理成繁體中文介紹，可推送 Telegram，並用 GitHub Pages 顯示當期與歷史日報。

**目前自動排程已暫停，只保留 GitHub Actions 手動執行。**舊文件提到的「每天台灣時間 11:00」已不符合目前 `daily.yml`；本次只更新 README，不重新啟用排程或執行日報。

## 主要功能與現況

| 功能 | 現況 |
| --- | --- |
| 熱門專案收集 | `scripts/crawler.py` 讀取 GitHub Trending。 |
| 中文介紹 | 使用模型，依專案名稱、描述及程式語言產生三句介紹。不是完整下載原始碼後的技術審查。 |
| Telegram | 設定啟用時發送本次日報。 |
| 靜態網站 | `index.html`、`app.js`、`style.css` 讀取 repo 內的 JSON，沒有常駐 Web 後端或資料庫。 |
| 歷史資料 | 保存當期 `news.json`、日期索引與每日 archive。 |
| AI 關鍵字篩選 | 有 `filter.py` 工具，但目前主流程沒有呼叫；修改 `ai_keywords` 不會把輸出自動限制為 AI-only。 |

## 系統架構

```text
手動執行 .github/workflows/daily.yml
  → Python 3.11 → scripts/run_all.py
      → GitHub Trending → 繁體中文摘要
      → data/news.json
      → data/archive/YYYY-MM-DD.json
      → data/index.json
      → 依設定發送 Telegram
  → github-actions[bot] 提交更新的 data/
  → GitHub Pages 讀取靜態檔與 JSON
```

`run_all.py` 負責資料與通知；Git commit／push 是 workflow 後續步驟，不是本機執行腳本就必然會推送 Git。網站目前是否已完成 Pages 發布，仍需另外查看部署狀態。

## 搜尋來源與判斷順序

### 資料來源只有 GitHub Trending

本流程不是全網搜尋，也沒有 Reddit、X 或新聞來源作備援。取得 Trending 清單後，直接送入摘要流程；目前不經過 `filter.py`，不應把日報標示為已通過 AI 專案篩選。

摘要使用的是 crawler 提供的名稱、描述與語言，不會自動讀取每個 repo 全部 README、程式碼或議題。因此介紹可作初步導覽，不能當成功能驗證。

### 模型依設定順序尝試

```text
讀 config.json 的 llm_models
  → 排除以 // 開頭的停用項目
  → 依剩餘清單順序呼叫
      groq/ 開頭 → Groq
      其他名稱 → Gemini 路徑
  → 第一個成功結果：整理輸出後使用
  → 失敗才試下一個啟用模型
  → 全部失敗：摘要留空，model_used 記為 none
```

目前只有 `groq/llama-3.3-70b-versatile` 啟用。兩個 Gemma 項目仍以 `//` 停用，**不是現在可用的自動備援**。workflow 也只注入 Groq 所需的 key；新增 Gemini 模型前，必須同步處理其環境設定。

輸出整理先找程式支援的精煉句格式，再找符合條件的中文段落，再用較寬鬆的中文段落判斷；都無法抽取時保留原輸出。因此「三句繁中」是 prompt 目標及清理規則，不是所有回應必然符合的保證。依據：[`scripts/summarize.py`](scripts/summarize.py)。

### 通知與日期

`notifications.telegram` 決定是否發送 Telegram。現行 `check_keys()` 即使關閉通知，仍會要求 Telegram token 與 chat ID；不能只改成 `false` 就假設不再需要這些環境值。

日報日期以 UTC+8 計算；同一天再次執行會寫回當天 archive，不是每次執行都保留一份新的時間戳檔。完整順序見 [`scripts/run_all.py`](scripts/run_all.py)。

## 套件與版本

| 元件 | repo 宣告 | 用途 |
| --- | --- | --- |
| Python | Actions `3.11`，未固定 patch | 執行日報腳本。 |
| requests | `2.31.0`，固定 | 抓取與 API 請求。 |
| Beautiful Soup | `4.12.3`，固定 | HTML 解析。 |
| python-dotenv | `1.0.1`，固定 | 本機環境值載入。 |
| actions/checkout | `@v4` | 取得 repo；major tag 不是 commit 鎖定。 |
| actions/setup-python | `@v5` | 建立 Actions Python 環境。 |
| 前端 | 原生 HTML／JavaScript／CSS | 不需 npm 或框架建置。 |
| Groq／Gemini／Telegram | 以 HTTP API 呼叫，沒有另外安裝對應 SDK | 模型與通知接線。 |

以上來自 [`requirements.txt`](requirements.txt) 與 [`daily.yml`](.github/workflows/daily.yml)，不是上游最新版本，也不代表本次已驗證服務可用性。

## 設定與本機操作

設定正本為 [`config.json`](config.json)。目前 workflow 需要 `GROQ_API_KEY`、`TELEGRAM_BOT_TOKEN`、`TELEGRAM_CHAT_ID`，實際值留在 GitHub Secrets 或本機 `.env`，不進 Git。

本 repo 原有操作說明未提供 `.env.example`，不要照抄其他專案的範本。模型程式使用 `load_dotenv(override=True)`，本機 `.env` 可能覆蓋既有同名環境變數；執行前先確認使用哪一組設定。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 已確認要查外站、呼叫模型、寫 data/ 及可能推送 Telegram 時才執行
python scripts/run_all.py
```

不要把這個完整入口当作唯讀測試；它載入時就會檢查 key，也可能建立資料目錄。一般程式檢查應與真實外站、模型、通知驗證分開。

## 目錄與文件

| 路徑 | 用途 |
| --- | --- |
| `.github/workflows/daily.yml` | 現行手動 workflow、環境與資料提交。 |
| `scripts/crawler.py`、`summarize.py`、`notify.py` | 抓取、摘要、推送。 |
| `scripts/run_all.py` | 完整流程入口。 |
| `scripts/filter.py` | 尚未接入主流程的篩選工具。 |
| `data/` | 自動產出資料，日常文件修改不順便重寫。 |
| [MANUAL.md](MANUAL.md) | 長版操作說明；排程是否啟用以現行 workflow 為準。 |
| [AGENTS.md](AGENTS.md) | 修改範圍、外部副作用與驗證要求。 |

本次只核對來源並更新 README，沒有手動觸發 workflow、重新抓 Trending、產生日報、發送 Telegram或檢查 Pages 正式環境。
