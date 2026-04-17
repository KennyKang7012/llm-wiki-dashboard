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

---

## AI Dashboard（QA 問答）

已提供本機版 Dashboard：

- 後端：`dashboard/server.py`
- 前端：`dashboard/static/`

啟動方式：

```powershell
python dashboard/server.py
```

開啟瀏覽器：

```text
http://127.0.0.1:8787
```

模式說明：

- `LLM_MODE=retrieval`：純檢索模式。
- `LLM_MODE=openai`：使用 OpenAI Responses API。
- `LLM_MODE=openai_compatible`：使用 OpenAI 相容 API（可接 Ollama）。
- `LLM_MODE=auto`：自動判斷（有 OpenAI Key 則用 OpenAI；否則若有自訂 `LLM_BASE_URL` 則走相容 API）。

### 使用 OpenAI

```powershell
$env:LLM_MODE = "openai"
$env:OPENAI_API_KEY = "你的金鑰"
$env:LLM_MODEL = "gpt-5.4-mini"
python dashboard/server.py
```

### 使用 Ollama（OpenAI 相容）

先確認本機 Ollama 已啟動且模型可用（例如 `qwen2.5:7b`）。

```powershell
$env:LLM_MODE = "openai_compatible"
$env:LLM_BASE_URL = "http://127.0.0.1:11434/v1"
$env:LLM_MODEL = "qwen2.5:7b"
# Ollama 通常不需要金鑰，留空即可
$env:LLM_API_KEY = ""
python dashboard/server.py
```

