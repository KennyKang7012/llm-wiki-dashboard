# LLM Wiki

一種使用 LLM 建立個人知識庫的模式。

這是一份概念文件，設計上可直接複製貼上到你自己的 LLM Agent（例如 OpenAI Codex、Claude Code、OpenCode / Pi 等）。它的目標是傳達高層次想法；至於具體細節，會由你的 agent 與你協作完成。

## 核心概念

多數人使用 LLM 與文件的方式很像 RAG：你上傳一批檔案，LLM 在查詢時擷取相關片段並生成答案。這樣做可行，但 LLM 每次提問都在從零重新發現知識。沒有累積性。當你問一個需要綜合五份文件的細緻問題時，LLM 每次都得重新找出並拼接相關片段。沒有任何內容被持續建立。NotebookLM、ChatGPT 檔案上傳，以及大多數 RAG 系統都屬於這種模式。

這裡的想法不同。不是只在查詢時從原始文件擷取內容，而是由 LLM **逐步建立並維護一個持久化的 wiki**：它是一組有結構、彼此連結的 markdown 檔案，位在你與原始來源之間。當你新增來源時，LLM 不只是為了日後檢索去建立索引，而是會讀取內容、抽取關鍵資訊，並整合進現有 wiki：更新實體頁、修訂主題摘要、標記新資料與舊主張的衝突、強化或挑戰持續演進的綜合結論。知識只需編譯一次，然後持續維持最新，而不是每次查詢都重新推導。

關鍵差異在這裡：**wiki 是一個可持續累積、會複利成長的產物。** 交叉連結已經存在，矛盾已被標記，綜合結論也已反映你讀過的內容。你每新增一份來源、每提出一個問題，wiki 都會更完整。

你幾乎不需要親自撰寫 wiki（或很少需要）—— 全部由 LLM 撰寫與維護。你負責蒐集來源、探索與提出正確問題。LLM 會處理所有繁重工作：摘要、交叉連結、歸檔與維護紀錄，這些正是知識庫能長期發揮價值的關鍵。實務上，我通常一邊開著 LLM agent，另一邊開著 Obsidian。LLM 會根據我們的對話直接修改內容，而我即時瀏覽結果：追連結、看 graph view、讀更新後頁面。Obsidian 是 IDE；LLM 是 programmer；wiki 是 codebase。

這種方式可套用在很多情境。以下是一些例子：

- **Personal**：追蹤你的目標、健康、心理與自我成長—— 將日記、文章、podcast 筆記歸檔，逐步建立一幅有結構的自我圖像。
- **Research**：在數週或數月內深挖一個主題—— 閱讀論文、文章、報告，逐步建立一份完整 wiki，並持續演進核心論點。
- **Reading a book**：邊讀邊整理每章內容，建立角色、主題、情節線及其關聯頁面。讀完時你就會有一份豐富的伴讀 wiki。可以想像像 [Tolkien Gateway](https://tolkiengateway.net/wiki/Main_Page) 這類 fan wiki—— 由志工社群花多年建立、包含數千個互相連結頁面，涵蓋角色、地點、事件、語言。你也可以在閱讀時個人化建立類似系統，由 LLM 負責交叉連結與維護。
- **Business/team**：由 LLM 維護的內部 wiki，資料來源可包含 Slack 討論串、會議逐字稿、專案文件、客戶通話。也可以讓人類參與審核更新。wiki 能保持最新，因為維護工作由 LLM 承擔，不再落在團隊不想做的瑣事上。
- **Competitive analysis、due diligence、trip planning、course notes、hobby deep-dives** —— 任何需要長期累積知識，且希望有系統整理而不是零散分布的情境。

## 架構

有三層：

**Raw sources** —— 你精選的來源文件集合。文章、論文、圖片、資料檔。這一層不可變更（immutable）—— LLM 只讀取，不修改。這是你的 source of truth。

**The wiki** —— 由 LLM 生成的 markdown 檔案目錄。包含摘要、實體頁、概念頁、比較頁、總覽與綜合分析。LLM 完全擁有這一層：建立頁面、在新來源到來時更新、維護交叉連結，並保持整體一致性。你負責閱讀；LLM 負責寫作。

**The schema** —— 一份文件（例如給 Claude Code 的 `CLAUDE.md` 或給 Codex 的 `AGENTS.md`），用來告訴 LLM wiki 的結構、慣例，以及在納入來源、回答問題、維護 wiki 時該遵循的工作流程。這是關鍵設定檔—— 它讓 LLM 成為有紀律的 wiki 維護者，而不只是通用 chatbot。你與 LLM 會隨時間共同演進這份 schema，找出最適合你領域的做法。

## 運作流程

**Ingest。** 你把新來源放進 raw collection，並請 LLM 處理。典型流程是：LLM 讀取來源、和你討論重點、在 wiki 寫摘要頁、更新索引、更新相關實體與概念頁，最後在 log 追加一筆紀錄。單一來源可能會影響 10-15 個 wiki 頁面。就我個人而言，我偏好一次 ingest 一份來源並保持參與—— 我會讀摘要、檢查更新，並引導 LLM 該強調哪些點。不過你也可以一次批次 ingest 多份來源、降低監督程度。你可以發展出適合自己風格的 workflow，並把它記錄在 schema 中，供後續 session 使用。

**Query。** 你針對 wiki 發問。LLM 會搜尋相關頁面、讀取內容，並附引用產出綜合答案。答案形式可依問題而異—— markdown 頁、比較表、簡報（Marp）、圖表（matplotlib）、canvas。關鍵洞察是：**高品質答案可以回寫到 wiki，成為新頁面。** 你要求的比較、某次分析、剛發現的關聯—— 這些都很有價值，不該消失在聊天紀錄裡。如此一來，你的探索也會像 ingest 的來源一樣，在知識庫中持續累積。

**Lint。** 定期請 LLM 對 wiki 做健康檢查。檢查項目包括：頁面間矛盾、已被新來源推翻卻未更新的陳述、沒有入站連結的孤兒頁、已被提及但尚未建立獨立頁面的重要概念、缺失的交叉連結、可透過 web search 補齊的資料缺口。LLM 很擅長提出下一步值得研究的問題與可新增的來源。這能讓 wiki 在擴張過程中維持健康。

## 索引與記錄

有兩個特殊檔案可幫助 LLM（以及你）在 wiki 成長時仍能有效導航。兩者用途不同：

**index.md** 以內容導向為主。它是 wiki 內容總目錄—— 每頁都列出連結、一句摘要，並可選擇附上日期、來源數等 metadata。通常依類別整理（entities、concepts、sources 等）。LLM 每次 ingest 都會更新它。在回答 query 時，LLM 先讀 index 找相關頁面，再深入閱讀。這在中等規模（約 100 份來源、數百頁）下效果出奇地好，而且不需要 embedding-based RAG 基礎設施。

**log.md** 以時間序為主。它是 append-only 的事件紀錄：發生了什麼、何時發生—— 包括 ingest、query、lint。實用技巧：若每筆紀錄都用一致前綴開頭（例如 `## [2026-04-02] ingest | Article Title`），就能用簡單 unix 工具解析；像 `grep "^## \[" log.md | tail -5` 可直接取得最近 5 筆。log 提供 wiki 演進時間軸，也能幫助 LLM 理解近期已完成的工作。

## 可選：CLI 工具

在某個階段，你可能會想建立一些小工具，讓 LLM 更有效率地操作 wiki。最明顯的是 wiki 頁面搜尋引擎—— 小規模時 index 檔就夠，但隨 wiki 成長你會需要更正式的搜尋能力。[qmd](https://github.com/tobi/qmd) 是不錯選項：它是針對 markdown 檔案的本地搜尋引擎，支援 hybrid BM25/vector search 與 LLM re-ranking，且全部在本機運作。它同時提供 CLI（LLM 可透過 shell 呼叫）與 MCP server（LLM 可當作原生工具使用）。你也可以自己做更簡單版本—— 有需要時，LLM 能協助你 vibe-code 一支簡單搜尋腳本。

## Tips and tricks

- **Obsidian Web Clipper** 是可把網頁文章轉成 markdown 的瀏覽器擴充套件。很適合快速把來源放進 raw collection。
- **Download images locally.** 在 Obsidian Settings → Files and links，把「Attachment folder path」設為固定目錄（例如 `raw/assets/`）。接著到 Settings → Hotkeys，搜尋「Download」，找到「Download attachments for current file」並綁定快捷鍵（例如 Ctrl+Shift+D）。剪藏完文章後按下快捷鍵，所有圖片就會下載到本機。這是可選步驟，但很實用—— LLM 可直接查看與引用圖片，而不必依賴可能失效的 URL。請注意，LLM 無法在單一步驟中原生讀取含 inline images 的 markdown；常見做法是先讀文字，再額外查看部分或全部引用圖片以補足上下文。雖然有點笨重，但實務上夠用。
- **Obsidian 的 graph view** 是觀察 wiki 結構最好的方式—— 哪些頁面互相連結、哪些是 hub、哪些是 orphan。
- **Marp** 是 markdown-based 的簡報格式，Obsidian 有對應 plugin。很適合直接從 wiki 內容生成簡報。
- **Dataview** 是 Obsidian plugin，可對頁面 frontmatter 執行查詢。若你的 LLM 會為 wiki 頁加上 YAML frontmatter（tags、dates、source counts），Dataview 就能產生動態表格與清單。
- wiki 本質上就是一個由 markdown 檔案構成的 Git repo。你會免費得到 version history、branching 與 collaboration。

## 為什麼這個方法有效

維護知識庫最耗人的部分，不是閱讀也不是思考，而是維護雜務（bookkeeping）。更新交叉連結、維持摘要最新、標記新資料何時推翻舊主張、讓數十頁內容保持一致。人們放棄 wiki，通常是因為維護成本增長速度快於其價值。LLM 不會感到無聊、不會忘記補交叉連結，而且能一次處理 15 個檔案。wiki 能持續被維護，是因為維護成本接近零。

人類的工作是精選來源、引導分析、提出好問題，並思考這些內容的意義。LLM 的工作則是其餘全部。

這個想法在精神上與 Vannevar Bush 的 Memex（1945）相近—— 一個個人化、經策展的知識儲存系統，文件之間透過關聯路徑連結。Bush 的願景其實更接近這種模式，而不是今日的 web：私有、主動策展，且文件間連結本身與文件同樣重要。他當年無法解決的是：誰來做維護？LLM 正好能處理這件事。


## 註記

這份文件刻意保持抽象。它描述的是一種模式，而不是特定實作。實際目錄結構、schema 慣例、頁面格式、tooling，都取決於你的領域、偏好與所選 LLM。上面提到的所有項目都可選且可模組化—— 保留有用的，忽略不需要的。舉例來說：如果你的來源都是純文字，你可能完全不需要圖片處理。若 wiki 規模很小，可能只靠 index 檔就足夠，不必建搜尋引擎。你也可能不在意簡報，只想要 markdown 頁面；或想要完全不同的輸出格式。正確用法是把這份文件交給你的 LLM agent，與它一起實作出適合你的版本。這份文件唯一的任務是傳達這個模式。其餘細節，LLM 可以自行補完。
