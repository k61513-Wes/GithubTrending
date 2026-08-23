# Tasks — [feature-slug]

> 活狀態文件：每完成一項就打勾。
> standard change 的跨 session / Agent resume 真相；接續時先讀本檔，再從第一個未完成項繼續。

slug:          [feature-slug]
current_phase: plan
track:         standard
danger_check:  none
stages:        [build, check, ship]
check_scope:   full
base_sha:      <plan 起點 SHA 或 UNBORN>
baseline_tests: unknown
expected_paths: []
checkpoint_commit: false

---

## Task 清單

- [ ] TASK-001　[描述]　｜影響：src/xxx　｜驗收：AC-001

## 驗收標準（Acceptance）

- AC-001：使用者可以 [具體操作]，系統回應 [具體結果]

---

## ⚠️ Tripwire（全程有效）

實作或驗證中若發現新命中且尚未在 proposal / flow plan 揭露並獲批准的危險項目、範圍擴張、設計決策或不可逆動作，停止並把缺口記進本檔。已揭露並批准的風險依 `danger_check` 與 proposal 執行對應驗證。

## 進度紀錄（給下一棒）

-
