from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import List
from urllib import error, request


ROOT_DIR = Path(__file__).resolve().parents[1]
WIKI_DIR = ROOT_DIR / "wiki"
STATIC_DIR = Path(__file__).resolve().parent / "static"


def load_dotenv_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().lstrip("\ufeff")
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_dotenv_file(ROOT_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT_SECONDS", "60"))

LLM_MODE = os.getenv("LLM_MODE", "auto").strip().lower()
LLM_MODEL = os.getenv("LLM_MODEL", OPENAI_MODEL).strip() or OPENAI_MODEL
LLM_API_KEY = os.getenv("LLM_API_KEY", OPENAI_API_KEY).strip()
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")


@dataclass
class Doc:
    rel_path: str
    title: str
    text: str
    text_lower: str


def load_wiki_docs() -> List[Doc]:
    docs: List[Doc] = []
    if not WIKI_DIR.exists():
        return docs

    for file_path in sorted(WIKI_DIR.rglob("*.md")):
        rel_path = file_path.relative_to(ROOT_DIR).as_posix()
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        title = text.splitlines()[0].lstrip("# ").strip() if text.strip() else file_path.stem
        docs.append(
            Doc(
                rel_path=rel_path,
                title=title,
                text=text,
                text_lower=text.lower(),
            )
        )
    return docs


DOCS = load_wiki_docs()


def _cjk_bigrams(text: str) -> List[str]:
    chars = re.findall(r"[\u4e00-\u9fff]", text)
    return [chars[i] + chars[i + 1] for i in range(len(chars) - 1)]


def query_terms(question: str) -> List[str]:
    terms = re.findall(r"[A-Za-z0-9_]+", question.lower())
    cjk_chars = re.findall(r"[\u4e00-\u9fff]", question)
    terms.extend(cjk_chars)
    terms.extend(_cjk_bigrams(question))

    deduped: List[str] = []
    seen = set()
    for term in terms:
        if term and term not in seen:
            seen.add(term)
            deduped.append(term)
    return deduped


def score_doc(doc: Doc, terms: List[str]) -> int:
    score = 0
    title_lower = doc.title.lower()
    for term in terms:
        t = term.lower()
        hits = doc.text_lower.count(t)
        if hits:
            score += hits
        if t in title_lower:
            score += 4
    return score


def retrieve_docs(question: str, top_k: int = 4) -> List[Doc]:
    terms = query_terms(question)
    if not DOCS:
        return []

    ranked = sorted(((score_doc(doc, terms), doc) for doc in DOCS), key=lambda x: x[0], reverse=True)
    positive = [doc for score, doc in ranked if score > 0]

    if positive:
        return positive[:top_k]
    return [doc for _, doc in ranked[:top_k]]


def short_excerpt(text: str, max_chars: int = 1200) -> str:
    compact = re.sub(r"\n{3,}", "\n\n", text.strip())
    if len(compact) <= max_chars:
        return compact
    return compact[:max_chars] + "\n..."


def retrieval_only_answer(question: str, docs: List[Doc]) -> str:
    if not docs:
        return "目前 wiki 中沒有可用內容，請先新增或 ingest 筆記。"

    lines = ["我先用 wiki 檢索模式回答（目前未啟用 LLM）。", "", f"問題：{question}", "", "相關內容："]
    for idx, doc in enumerate(docs, start=1):
        lines.append(f"{idx}. {doc.title}（{doc.rel_path}）")
    lines.append("")
    lines.append("建議：設定 LLM_MODE 與模型參數後可改為 AI 綜合回答模式。")
    return "\n".join(lines)


def resolved_llm_mode() -> str:
    if LLM_MODE in ("retrieval", "openai", "openai_compatible"):
        return LLM_MODE

    if OPENAI_API_KEY:
        return "openai"

    # auto mode fallback: when base URL is customized, assume openai-compatible provider.
    if LLM_BASE_URL != "https://api.openai.com/v1":
        return "openai_compatible"

    return "retrieval"


def llm_enabled() -> bool:
    mode = resolved_llm_mode()
    if mode == "openai":
        return bool(OPENAI_API_KEY or LLM_API_KEY)
    if mode == "openai_compatible":
        return bool(LLM_MODEL and LLM_BASE_URL)
    return False


def build_prompt(question: str, docs: List[Doc]) -> str:
    context_blocks = []
    for doc in docs:
        context_blocks.append(f"[來源: {doc.rel_path}]\n{short_excerpt(doc.text, max_chars=1400)}")

    return (
        "你是使用繁體中文回答的知識助理。"
        "請根據提供的 wiki 內容回答問題，避免編造。"
        "若資訊不足請明確指出。"
        "回答末段請列出使用到的來源路徑清單。\n\n"
        f"問題：{question}\n\n"
        "wiki 內容：\n"
        + "\n\n".join(context_blocks)
    )


def _http_post_json(url: str, payload: dict, timeout_sec: int, api_key: str = "") -> dict:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    with request.urlopen(req, timeout=timeout_sec) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def call_openai_responses(prompt: str) -> str:
    api_key = LLM_API_KEY or OPENAI_API_KEY
    payload = {
        "model": LLM_MODEL,
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            }
        ],
    }

    data = _http_post_json(
        "https://api.openai.com/v1/responses",
        payload,
        timeout_sec=OPENAI_TIMEOUT,
        api_key=api_key,
    )

    output_text = data.get("output_text", "").strip()
    if output_text:
        return output_text

    parts = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                parts.append(text)
    return "\n".join(parts).strip()


def call_openai_compatible_chat(prompt: str) -> str:
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "你是使用繁體中文回答的知識助理。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    data = _http_post_json(
        f"{LLM_BASE_URL}/chat/completions",
        payload,
        timeout_sec=OPENAI_TIMEOUT,
        api_key=LLM_API_KEY,
    )

    choices = data.get("choices", [])
    if not choices:
        return ""

    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, str):
        return content.strip()

    # Some providers may return list chunks.
    parts: List[str] = []
    if isinstance(content, list):
        for item in content:
            text = item.get("text") if isinstance(item, dict) else ""
            if text:
                parts.append(text)
    return "\n".join(parts).strip()


def call_llm(question: str, docs: List[Doc]) -> str:
    prompt = build_prompt(question, docs)
    mode = resolved_llm_mode()

    if mode == "openai":
        return call_openai_responses(prompt)
    if mode == "openai_compatible":
        return call_openai_compatible_chat(prompt)

    return ""


class DashboardHandler(BaseHTTPRequestHandler):
    def _json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_file(self, file_path: Path, content_type: str) -> None:
        if not file_path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            return self._serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
        if self.path == "/app.js":
            return self._serve_file(STATIC_DIR / "app.js", "application/javascript; charset=utf-8")
        if self.path == "/styles.css":
            return self._serve_file(STATIC_DIR / "styles.css", "text/css; charset=utf-8")
        if self.path == "/api/health":
            mode = resolved_llm_mode()
            return self._json(
                {
                    "ok": True,
                    "docs": len(DOCS),
                    "mode": mode if llm_enabled() else "retrieval",
                    "llm_mode": mode,
                    "model": LLM_MODEL,
                    "base_url": LLM_BASE_URL if mode == "openai_compatible" else "https://api.openai.com/v1",
                }
            )
        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self) -> None:
        if self.path != "/api/ask":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            body = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            return self._json({"error": "JSON 格式錯誤"}, status=400)

        question = (body.get("question") or "").strip()
        if not question:
            return self._json({"error": "請輸入問題"}, status=400)

        docs = retrieve_docs(question, top_k=4)
        sources = [{"title": d.title, "path": d.rel_path} for d in docs]

        if not llm_enabled():
            answer = retrieval_only_answer(question, docs)
            return self._json({"mode": "retrieval", "answer": answer, "sources": sources})

        try:
            answer = call_llm(question, docs)
            if not answer:
                answer = "模型沒有回傳內容，請稍後再試。"
            return self._json({"mode": resolved_llm_mode(), "answer": answer, "sources": sources})
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            fallback = retrieval_only_answer(question, docs)
            return self._json(
                {
                    "mode": "retrieval",
                    "answer": fallback,
                    "sources": sources,
                    "warning": f"LLM API 錯誤（HTTP {exc.code}），已改用檢索模式。",
                    "detail": detail[:500],
                }
            )
        except Exception as exc:
            fallback = retrieval_only_answer(question, docs)
            return self._json(
                {
                    "mode": "retrieval",
                    "answer": fallback,
                    "sources": sources,
                    "warning": f"LLM 呼叫失敗：{exc}，已改用檢索模式。",
                }
            )


def run() -> None:
    host = os.getenv("DASHBOARD_HOST", "127.0.0.1")
    port = int(os.getenv("DASHBOARD_PORT", "8787"))
    server = ThreadingHTTPServer((host, port), DashboardHandler)

    mode = resolved_llm_mode()
    print(f"AI Dashboard running at http://{host}:{port}")
    print(f"Wiki documents loaded: {len(DOCS)}")
    print(f"Mode: {mode if llm_enabled() else 'retrieval'}")
    print(f"Model: {LLM_MODEL}")
    if mode == "openai_compatible":
        print(f"Base URL: {LLM_BASE_URL}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    run()
