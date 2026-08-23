# Constitution — GithubTrending 專案專屬規則

> 本檔只放 GithubTrending 專屬、違反就會造成錯誤的規則。跨專案安全與 DevFlow stage 契約由 Global AGENTS 與共用 Skill 提供。

## 7. 架構不變量

- 自動化主線為 `.github/workflows/daily.yml` → `scripts/run_all.py` → `data/news.json` / `data/index.json` / `data/archive/` → Telegram → bot commit/push。
- `data/` 的每日 JSON 是 pipeline 產物；修程式時不要把手工編輯產出檔當成主要修法，除非任務本身就是資料修復。
- `scripts/run_all.py` 具有外部網路、資料寫入與通知副作用，不是 read-only check。
- workflow 的 bot write 權限只授權既有自動化；互動式 Agent 仍受當次 Git 權限邊界約束。
- Secret 名稱與 provider 選擇要和 workflow、config、scripts、README 對齊；實際 secret 值永不進 repo。

## 8. 危險項目

以下變更命中任一項時走 standard，並在 `danger_check` 記錄實際風險：

- GitHub Actions 排程、permissions、bot commit/push
- Telegram 通知與目標 chat
- LLM provider / model / API key 名稱
- GitHub Trending crawler / 外部來源與 retry
- `data/` schema、archive/index 相容性
- 任何會讓本地測試觸發外部通知或寫入正式資料的變更

## 9. 驗證規範

- 優先使用 source-level / syntax / 可離線驗證；只有任務需要時才做真實 crawler、LLM 或 Telegram E2E。
- 真實 `scripts/run_all.py` 會改檔並通知，執行前要明確取得授權，完成後要回報實際副作用。
- 修改 workflow / config / README 相關契約時，需檢查四者是否有互相矛盾的 schedule、secret 或 provider 描述。
- 未執行 workflow 或外部服務時，不得宣稱排程、LLM、Telegram 已 runtime 驗證。

## 10. Release / Preflight 邊界

- `df-5-preflight` 只判斷 release/readiness，不執行完整 pipeline。
- GithubTrending 目前未設定固定唯讀 target preflight command；`Target check` 預設為「未設定」。
- Preflight 不得 dispatch workflow、執行 `scripts/run_all.py`、發送 Telegram、修改 `data/`、commit 或 push。
