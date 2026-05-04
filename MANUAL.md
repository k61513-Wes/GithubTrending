# GitHub Trending AI 日報系統｜使用手冊

> 最後更新：2026-05-04
> 網站網址：https://k61513-wes.github.io/GithubTrending
> Repo 網址：https://github.com/k61513-Wes/GithubTrending

---

## 目錄

1. [系統簡介](#1-系統簡介)
2. [運作流程](#2-運作流程)
3. [檔案結構說明](#3-檔案結構說明)
4. [日常使用：你只需要管這兩個檔案](#4-日常使用你只需要管這兩個檔案)
5. [手動執行（本地測試）](#5-手動執行本地測試)
6. [GitHub Actions 自動排程](#6-github-actions-自動排程)
7. [Telegram 推播格式](#7-telegram-推播格式)
8. [網站前端說明](#8-網站前端說明)
9. [金鑰管理](#9-金鑰管理)
10. [常見問題排查](#10-常見問題排查)
11. [成本說明](#11-成本說明)

---

## 1. 系統簡介

這是一套**全自動 AI 科技日報系統**，每天早上 09:00（台灣時間）自動執行以下工作：

- 抓取 GitHub Trending 當日熱門專案（約 25 筆）
- 過濾出 AI / LLM 相關專案（約 5–10 筆）
- 使用 Gemini / Gemma 模型生成**繁體中文摘要**
- 透過 **Telegram Bot** 推播每日日報
- 更新 **GitHub Pages 網站**，保留完整歷史日報

**運行成本：$0**（全部使用免費方案）

---

## 2. 運作流程

```
每天早上 09:00（台灣時間）
        ↓
GitHub Actions 觸發排程
        ↓
[步驟 1] crawler.py   — 爬取 GitHub Trending（25 筆）
        ↓
[步驟 2] filter.py    — 關鍵字過濾，留下 AI 相關（5–10 筆）
        ↓
[步驟 3] summarize.py — 呼叫 Gemini API，生成繁體中文摘要
        ↓
[步驟 4] run_all.py   — 輸出 news.json、備份至 archive/、更新 index.json
        ↓
[步驟 5] notify.py    — Telegram Bot 逐一推播每個專案
        ↓
[步驟 6] GitHub Actions git push 回 repo
        ↓
GitHub Pages 自動更新，網站顯示今日日報
```

---

## 3. 檔案結構說明

```
GithubTrending/
│
├── config.json                  ← ⭐ 主要設定檔（關鍵字、模型開關）
│
├── scripts/
│   ├── crawler.py               ← 爬蟲：抓取 GitHub Trending
│   ├── filter.py                ← 過濾：AI 關鍵字比對
│   ├── summarize.py             ← 摘要：呼叫 Gemini API
│   ├── notify.py                ← 推播：Telegram Bot
│   └── run_all.py               ← 主程式：依序串接所有步驟
│
├── data/
│   ├── news.json                ← 當日資料（每天自動覆蓋）
│   ├── index.json               ← 歷史日期清單（前端切換用）
│   └── archive/
│       └── YYYY-MM-DD.json      ← 每日備份（永久保留）
│
├── .github/workflows/
│   └── daily.yml                ← GitHub Actions 排程設定
│
├── index.html                   ← 網站首頁
├── style.css                    ← 網站樣式
├── app.js                       ← 網站邏輯
│
├── .env                         ← 本地金鑰（不 commit，已加入 .gitignore）
├── .env.example                 ← 金鑰範本（只有欄位名稱）
├── requirements.txt             ← Python 套件清單
└── MANUAL.md                    ← 本手冊
```

---

## 4. 日常使用：你只需要管這兩個檔案

### 4-1. `config.json`｜調整過濾規則與模型

這是唯一需要日常維護的設定檔，不需要動任何 Python 程式碼。

#### 模型開關（`llm_models`）

```json
"llm_models": [
  "//gemini-2.5-pro",     ← 前面加 // 代表停用（目前停用）
  "gemma-4-31b-it",       ← 啟用，第一優先
  "gemma-4-26b-a4b-it"    ← 啟用，第二備援
]
```

**規則：**
- 有 `//` 前綴 → 停用，程式會跳過
- 沒有 `//` → 啟用，依序嘗試
- 第一個啟用的模型為主力，失敗才自動換下一個
- 至少要有一個啟用的模型，否則程式會報錯

> ⚠️ 注意：`//` 必須在引號**裡面**，例如 `"//gemini-2.5-pro"`，
> 不能寫成 `// "gemini-2.5-pro"`（那是無效的 JSON）

**三個可用模型說明：**

| 模型 | 說明 | 特性 |
|------|------|------|
| `gemini-2.5-pro` | Google 最強推理模型 | 品質最佳，偶有額度限制 |
| `gemma-4-31b-it` | 開源 31B Dense 模型 | 品質接近 Pro，較穩定 |
| `gemma-4-26b-a4b-it` | 開源 26B MoE 模型 | 速度快，輕量備援 |

---

#### AI 過濾關鍵字（`ai_keywords`）

關鍵字分四個分類，每個分類可以自由新增或刪除：

```json
"ai_keywords": {
  "模型名稱": ["llm", "gpt", "claude", "gemini", ...],
  "技術術語": ["transformer", "rag", "embedding", ...],
  "應用場景": ["agent", "chatbot", "copilot", ...],
  "通用詞":   ["machine learning", "deep learning", ...]
}
```

**新增關鍵字範例：**
```json
"模型名稱": [
  "llm", "gpt", "claude", "gemini",
  "o3", "o4", "grok"    ← 直接加在這裡
]
```

**新增分類範例：**
```json
"硬體加速": ["cuda", "tpu", "tensorrt", "triton"]
```

**過濾邏輯：**
- 比對欄位：`description`（英文描述）+ `name`（專案名稱）
- 比對方式：不分大小寫，只要關鍵字出現在文字中任何位置即符合
- 25 筆 → 通常過濾後剩 5–10 筆

---

### 4-2. GitHub Secrets｜金鑰管理

前往：`GitHub Repo → Settings → Secrets and variables → Actions`

| Secret 名稱 | 說明 |
|------------|------|
| `GEMINI_API_KEY` | Gemini API 金鑰，用於生成中文摘要 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | 推播目標的 Chat ID |

> 金鑰更換後，下次 Actions 執行時自動生效，不需要其他操作。

---

## 5. 手動執行（本地測試）

### 環境準備（第一次）

```bash
# 1. 安裝套件
pip install -r requirements.txt

# 2. 建立 .env 檔（複製範本後填入真實金鑰）
cp .env.example .env
```

`.env` 內容：
```
GEMINI_API_KEY=你的_gemini_api_key
TELEGRAM_BOT_TOKEN=你的_bot_token
TELEGRAM_CHAT_ID=你的_chat_id
```

### 執行完整流程

```bash
python scripts/run_all.py
```

執行後會看到：
```
=== GitHub Trending AI 日報 (2026-05-04 09:15) ===

[1/5] 抓取 GitHub Trending...
  抓到 25 筆

[2/5] 過濾 AI 相關專案...
  過濾後剩 8 筆

[3/5] 生成繁體中文摘要...
  [1/8] 生成摘要：ollama/ollama
    [OK] gemma-4-31b-it
  ...

[4/5] 輸出 JSON 資料檔...
  [OK] 寫入 data/news.json
  [OK] 備份至 data/archive/2026-05-04.json
  [OK] 更新 index.json，共 3 筆日期

[5/5] Telegram 推播...
  [OK] Telegram 推播成功，共 10 則（標題 + 8 專案 + 結尾）

=== 完成 ===
```

### 只重跑 Telegram 推播（不重新抓資料）

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

### 排程時間

| 設定 | 說明 |
|------|------|
| Cron：`0 1 * * *` | UTC 01:00 = 台灣時間 09:00 |
| 每天執行一次 | 約消耗 3–4 分鐘（免費額度 2,000 分鐘/月） |

### 手動觸發

1. 前往：https://github.com/k61513-Wes/GithubTrending/actions
2. 點選左側 `Daily AI News`
3. 點選右上角 `Run workflow`
4. 確認後等待約 3–4 分鐘

### 執行成功的標誌

- Actions 頁面顯示 ✅ 綠色勾勾
- Telegram 收到當日推播
- `data/news.json` 的 `date` 欄位更新為今日日期
- `data/archive/` 新增今日備份檔案

### 執行後 git commit 格式

```
chore: update daily AI news 2026-05-04
```

---

## 7. Telegram 推播格式

每次推播分為多則訊息發送：

**第 1 則：標題**
```
📅 2026-05-04 AI 日報

今日共發現 8 個 AI 相關專案 🔥
```

**第 2–N 則：每個專案各一則**
```
1️⃣ ollama/ollama  ⭐ +523
🔧 Go

Ollama 是一款讓開發者在本機直接執行大型語言模型的工具，
支援 Llama、Gemma 等主流模型，免雲端即可體驗 AI 推論。
適合想在本地端安全運行 LLM 的開發者與 AI 研究人員使用。

🔗 https://github.com/ollama/ollama
```

**最後一則：網站連結**
```
🌐 完整日報：https://k61513-wes.github.io/GithubTrending
```

> 每則訊息間隔 0.5 秒發送，避免觸發 Telegram 速率限制。

---

## 8. 網站前端說明

**網址：** https://k61513-wes.github.io/GithubTrending

### 功能

| 功能 | 說明 |
|------|------|
| 當日日報 | 預設顯示今天的資料 |
| 歷史日報切換 | 右上角下拉選單，可查看過去每一天的資料 |
| 專案卡片 | 顯示名稱（可點擊跳轉）、語言、今日星星數、繁體中文摘要 |

### 資料來源

網站直接讀取 Repo 內的 JSON 檔案：

| 資料 | 對應檔案 |
|------|---------|
| 今日日報 | `data/news.json` |
| 歷史日期清單 | `data/index.json` |
| 歷史日報 | `data/archive/YYYY-MM-DD.json` |

> 每次 GitHub Actions 執行完畢後，網站約 1–2 分鐘內自動更新。

---

## 9. 金鑰管理

### 取得 Gemini API Key

1. 前往：https://aistudio.google.com/app/apikey
2. 建立新的 API Key
3. 填入 `.env` 或 GitHub Secrets

**免費額度：** 1,500 次 / 天（足夠每日執行使用）

### 取得 Telegram Bot Token

1. 在 Telegram 搜尋 `@BotFather`
2. 傳送 `/newbot`，依指示建立 Bot
3. 取得 Token（格式：`123456789:ABCdef...`）

### 取得 Telegram Chat ID

1. 先傳送任一訊息給你的 Bot
2. 在瀏覽器開啟：
   ```
   https://api.telegram.org/bot你的TOKEN/getUpdates
   ```
3. 找到 JSON 裡的 `"chat": {"id": 數字}`，那個數字就是 Chat ID

---

## 10. 常見問題排查

### Q：Telegram 收不到推播
| 可能原因 | 解法 |
|---------|------|
| 還沒傳訊息給 Bot | 先對 Bot 傳一則訊息，再重跑 |
| Chat ID 填錯 | 重新用 `getUpdates` 確認 |
| Bot Token 失效 | 向 BotFather 重新取得 Token |
| GitHub Secrets 沒有設定 | 確認三個 Secret 都有填 |

### Q：摘要品質差或包含英文推理過程
| 可能原因 | 解法 |
|---------|------|
| 備援模型輸出推理鏈 | 程式已有後處理自動過濾，若仍出現可在 config.json 停用該模型 |
| 所有模型額度耗盡 | 更換 Gemini API Key，或等隔日額度重置 |

### Q：GitHub Actions 執行失敗
| 錯誤訊息 | 解法 |
|---------|------|
| `exit code 128` | 確認 daily.yml 有 `permissions: contents: write` |
| `GEMINI_API_KEY 未設定` | 確認 GitHub Secrets 有填入正確金鑰 |
| `HTTP 429` | Gemini API 額度耗盡，更換 API Key |
| `chat not found` | Telegram Chat ID 填錯，重新確認 |

### Q：網站沒有更新
1. 確認 Actions 執行成功（綠色勾勾）
2. 確認 `data/news.json` 的日期是今天
3. 等待 1–2 分鐘讓 GitHub Pages 重新部署
4. 強制重新整理瀏覽器（Ctrl+Shift+R）

### Q：過濾到不相關的專案
- 編輯 `config.json` 的 `ai_keywords`，刪除或縮減太寬鬆的關鍵字
- `"ai"` 這個詞已預設移除（太容易誤判）

### Q：想新增更多 AI 關鍵字
- 編輯 `config.json` 的 `ai_keywords`，在對應分類加入新關鍵字
- push 後下次執行自動生效

---

## 11. 成本說明

| 服務 | 方案 | 費用 |
|------|------|------|
| GitHub Actions | 免費（2,000 分鐘/月，實際用量約 90–120 分鐘） | $0 |
| Gemini API | 免費（1,500 次/天，每日約用 5–10 次） | $0 |
| GitHub Pages | 免費靜態網站（Public Repo） | $0 |
| Telegram Bot API | 永久免費 | $0 |
| **每月總計** | | **$0** |
