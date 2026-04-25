---
name: local-git-commit
description: 針對本地端 Git commit 的安全流程技能：檢查變更、精準 stage、撰寫清楚 commit message，僅執行本地 commit，不做 push。
---

# Local Git Commit

## 適用情境

當使用者要求「幫我 commit」、「整理並提交這次變更」、「產生 commit 訊息並做本地提交」時使用。

## 核心原則

1. 僅做本地端 commit，不主動執行 `git push`。
2. 不做破壞性操作（例如 `git reset --hard`、`git checkout --`）除非使用者明確要求。
3. 只提交與本次任務相關的檔案，避免混入無關變更。
4. 若發現風險（大量非預期改動、衝突狀態、可疑二進位變更），先暫停並向使用者確認。
5. 預設使用繁體中文撰寫 commit message；僅在使用者明確要求時改用其他語言。

## 標準流程

1. 檢查工作樹狀態。
- 執行：`git status --short`
- 必要時補看：`git diff -- <path>`、`git diff --cached -- <path>`

2. 決定提交範圍。
- 優先只加入本次任務的檔案。
- 若變更可拆分，使用較小且語義清楚的 commit。

3. 精準 stage。
- 優先使用：`git add <path>`
- 需要互動式分塊時可用：`git add -p`

4. 建立 commit。
- 建議訊息格式：`<type>: <繁中摘要>`
- 常用 `type`：`feat`、`fix`、`refactor`、`docs`、`test`、`chore`
- summary 使用繁體中文現在式、具體描述行為（例如：`fix: 修正 wiki index 為空時的處理`）

5. 驗證結果並回報。
- 執行：`git show --stat --oneline -1`
- 回報 commit hash、訊息、涉及檔案。

## Commit 訊息規範

- 預設語言為繁體中文（台灣慣用語）；除非使用者另有指定。
- 第一行（subject）建議不超過 72 字元。
- 以「做了什麼」為主，避免模糊詞彙（如 update、misc changes）。
- 若需要 body，說明：
- 為什麼要改
- 主要改動點
- 可能影響範圍

## 風險檢查清單

提交前確認：

- 是否含機密資訊（`.env`、金鑰、token）
- 是否誤提交大型產物或暫存檔
- 是否有與本次任務無關的變更
- 是否已包含必要文件更新（若此專案有要求）

## 預設輸出

完成後回報：

- commit hash（短版）
- commit 訊息
- 變更檔案清單
- 是否仍有未提交變更
