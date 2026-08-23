# GithubTrending Agents Rules

本檔是 GithubTrending 專案的最高優先 Project rules 入口。

## 工作入口

- 每次開始工作先讀 `AGENTS.md`，再依任務補讀 `README.md`、`config.json`、`.github/workflows/daily.yml` 與 `scripts/`；只有使用者明確呼叫 `df-*` 時才另外讀 `.agent/constitution.md`。
- 若 README、workflow、config 與程式碼描述不一致，先列出差異，不自行選一份當成唯一真相。
- 只做原需求必要變更；`data/` 內每日產出預設視為自動化結果，不因一般程式修改順手改寫。

## 專案不變量

- 自動化主線為 GitHub Actions `daily.yml` → `python scripts/run_all.py` → 更新 `data/news.json`、`data/index.json`、`data/archive/` → Telegram 通知 → `github-actions[bot]` commit/push。
- `scripts/run_all.py` 不是唯讀檢查：它會做外部網路請求、寫入 `data/` 並可能發送 Telegram。分析、code review、df-5 preflight 不得自行執行。
- workflow 的既有 `contents: write` 與 bot push 是專案自動化權限，不代表互動式 Agent 取得 commit/push 權限。
- API key、Telegram token/chat id 等值只能來自 `.env` 或 GitHub Secrets，不得寫入 repo、log 或對話輸出。
- 修改 workflow 排程、Secrets 名稱、LLM provider/config、Crawler 或 Telegram 通知時，要同步檢查 README / config / scripts 是否仍一致。

## 驗證

- 純程式修改先做對應的 source-level / syntax / 可離線驗證；需要真正抓 GitHub Trending、呼叫 LLM 或發 Telegram 時，必須明確說明外部副作用並取得使用者授權。
- 修改資料 schema 時要同時檢查 Web 讀取端與 archive/index 相容性。
- 未實際跑 workflow 或真實外部服務時，不得宣稱每日排程、LLM 或 Telegram 已實測成功。

## AI 協作與 DevFlow

- 只有使用者明確呼叫 `df-*` 時才啟用 Agent DevFlow；流程以本機已安裝的共用 Skill 為正本，本 repo 不複製 stage 規則。
- DevFlow 執行時讀取 `AGENTS.md` 與 `.agent/constitution.md`；standard change 狀態存於 `.agent/changes/`。
- `df-5-preflight` 只判斷 release/readiness。GithubTrending 目前沒有固定唯讀 target preflight command；不得自行 dispatch workflow、執行 `scripts/run_all.py`、發 Telegram 或 commit/push。
