# LLM Wiki（繁體中文）

這個專案是一個可持續維護的個人知識庫系統。

核心做法：
- `raw/` 放原始來源（唯讀）
- `wiki/` 放由 LLM 維護的知識頁（可增量更新）
- `AGENTS.md` 定義 LLM 工作規範（架構、流程、格式）

---

## 目錄結構

```text
.
├─ README.md
├─ AGENTS.md
├─ llm-wiki.md
├─ raw/
│  ├─ README.md
│  ├─ sources/
│  │  └─ README.md
│  └─ assets/
│     └─ README.md
└─ wiki/
   ├─ index.md
   ├─ log.md
   ├─ 總覽.md
   ├─ 來源/
   │  └─ 來源總表.md
   ├─ 主題/
   │  └─ 主題地圖.md
   ├─ 實體/
   │  └─ 實體地圖.md
   ├─ 分析/
   │  └─ 起始盤點.md
   └─ templates/
      ├─ 來源摘要模板.md
      ├─ 主題頁模板.md
      └─ 實體頁模板.md
```

---

## 快速開始

1. 把第一份來源放到 `raw/sources/`。
2. 若來源有圖片，放到 `raw/assets/`。
3. 在與 LLM 的對話中下指令：

```text
請 ingest raw/sources/<檔名>
```

4. LLM 應自動完成：
- 建立或更新 `wiki/來源/<來源頁>.md`
- 更新主題/實體/分析頁
- 更新 `wiki/index.md`
- 追加一筆到 `wiki/log.md`

---

## 日常操作

### 1) Ingest（納入新來源）

```text
請 ingest raw/sources/2026-04-17_AI市場報告.md
```

### 2) Query（用 wiki 回答問題）

```text
根據目前 wiki，整理 AI 市場的三個關鍵趨勢，並附來源頁連結
```

若回答有長期價值，可要求：

```text
把這次回答存成 wiki/分析/AI市場三大趨勢.md，並更新 index 與 log
```

### 3) Lint（健康檢查）

```text
請對 wiki 做 lint：檢查矛盾、孤兒頁、缺少交叉連結，並修正可自動修正項目
```

---

## 撰寫與命名規範

- 所有 wiki 筆記一律使用繁體中文。
- `raw/` 原始內容原則上不修改。
- 檔名建議：`YYYY-MM-DD_主題_來源名稱.ext`
- wiki 連結建議使用 `[[頁名]]`（Obsidian 友善）。
- 每次大量更新後，必須同步更新：
  - `wiki/index.md`
  - `wiki/log.md`

---

## 推薦工具（可選）

- Obsidian：瀏覽 wiki、使用雙向連結與圖譜。
- Git：保留每次知識庫演進歷史。

---

## 重要檔案

- 規範：`AGENTS.md`
- 架構想法來源：`llm-wiki.md`
- 系統入口：`wiki/index.md`

