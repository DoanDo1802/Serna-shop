from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
from typing import List, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


def _repo_root_from_this_file() -> Path:
    # .../agent_sale/src/agent_sale/tools/hair_dryer_troubleshooting.py
    # repo root for this package is .../agent_sale
    return Path(__file__).resolve().parents[3]


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


@dataclass(frozen=True)
class _Chunk:
    source: str
    text: str


@dataclass(frozen=True)
class _EmbeddedChunk:
    source: str
    text: str
    vector: List[float]
    norm: float


def _chunk_markdown_by_headings(md: str) -> List[_Chunk]:
    """
    Lightweight chunking: split by Markdown headings (#, ##, ###).
    Keeps heading line as part of chunk for better context.
    """
    lines = md.splitlines()
    chunks: List[_Chunk] = []
    current_title: Optional[str] = None
    current_lines: List[str] = []

    def flush():
        nonlocal current_title, current_lines
        if not current_lines:
            return
        title = current_title or "Document"
        text = "\n".join(current_lines).strip()
        if text:
            chunks.append(_Chunk(source=title, text=text))
        current_lines = []

    for line in lines:
        if line.startswith("#"):
            flush()
            current_title = line.strip().lstrip("#").strip() or "Document"
            current_lines = [line]
        else:
            current_lines.append(line)

    flush()
    return chunks


def _score_chunk(query_terms: List[str], chunk_text_norm: str) -> int:
    score = 0
    for t in query_terms:
        if not t:
            continue
        if t in chunk_text_norm:
            score += 3
        # tiny boost for partial matches on longer terms
        if len(t) >= 6:
            stem = t[: max(4, len(t) // 2)]
            if stem and stem in chunk_text_norm:
                score += 1
    return score


def _cosine(a: List[float], a_norm: float, b: List[float], b_norm: float) -> float:
    if not a or not b:
        return -1.0
    denom = a_norm * b_norm
    if denom <= 0:
        return -1.0
    s = 0.0
    # assume same length; if not, compare shortest prefix
    for x, y in zip(a, b):
        s += x * y
    return s / denom


def _embed_with_gemini(text: str, task_type: str) -> List[float]:
    """
    Uses Gemini Embedding 2 (preview) via google-generativeai.
    Model name default: 'models/gemini-embedding-2-preview'
    """
    api_key = os.getenv("GOOGLE_API_KEY") or ""
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY")

    model_name = os.getenv("EMBEDDINGS_GOOGLE_GENERATIVE_AI_MODEL_NAME") or "gemini-embedding-2-preview"
    # Accept either "models/..." or raw name
    if model_name.startswith("models/"):
        model_name = model_name[len("models/") :]

    # Prefer the new supported SDK (`google-genai`).
    try:
        from google import genai  # type: ignore
    except Exception as e:
        raise RuntimeError(f"google-genai not installed: {e}")

    client = genai.Client(api_key=api_key)
    res = client.models.embed_content(
        model=model_name,
        contents=text,
    )

    # Try to extract a single embedding vector across SDK versions.
    embeddings = getattr(res, "embeddings", None)
    if embeddings and isinstance(embeddings, list):
        first = embeddings[0]
        values = getattr(first, "values", None)
        if values and isinstance(values, list):
            return [float(x) for x in values]

    # Fallback: dict-like
    if isinstance(res, dict):
        emb = res.get("embeddings")
        if isinstance(emb, list) and emb:
            first = emb[0]
            if isinstance(first, dict) and isinstance(first.get("values"), list):
                return [float(x) for x in first["values"]]

    raise RuntimeError("Empty embedding response")


class HairDryerTroubleshootingLookupInput(BaseModel):
    symptom: str = Field(..., description="Triệu chứng/mô tả lỗi, ví dụ: 'có gió nhưng không nóng'.")
    model: Optional[str] = Field(None, description="Model máy sấy tóc (nếu biết), ví dụ: 'HD-1800ION'.")
    top_k: int = Field(1, ge=1, le=5, description="Số đoạn liên quan muốn trả về.")


class HairDryerTroubleshootingLookupTool(BaseTool):
    name: str = "hair_dryer_troubleshooting_lookup"
    description: str = (
        "Tra cứu tài liệu kỹ thuật nội bộ về chẩn đoán/sửa máy sấy tóc. "
        "Dùng khi cần chuyển 'triệu chứng' thành checklist chẩn đoán và hướng sửa an toàn, kèm trích dẫn nguồn."
    )
    args_schema: Type[BaseModel] = HairDryerTroubleshootingLookupInput

    def __init__(self, knowledge_path: Optional[Path] = None):
        super().__init__()
        self._knowledge_path = knowledge_path or (
            _repo_root_from_this_file() / "knowledge" / "hair_dryer_troubleshooting.md"
        )
        self._cache_path = _repo_root_from_this_file() / "knowledge" / ".cache" / "hair_dryer_troubleshooting.embeddings.json"

    def _load_or_build_index(self, md: str) -> List[_EmbeddedChunk]:
        # Build a deterministic cache key based on content + embedding model name.
        model_name = os.getenv("EMBEDDINGS_GOOGLE_GENERATIVE_AI_MODEL_NAME") or "models/gemini-embedding-2-preview"
        cache_key = _sha256(f"{model_name}\n{md}")

        try:
            if self._cache_path.exists():
                payload = json.loads(self._cache_path.read_text(encoding="utf-8"))
                if payload.get("cache_key") == cache_key and isinstance(payload.get("chunks"), list):
                    out: List[_EmbeddedChunk] = []
                    for c in payload["chunks"]:
                        vec = c.get("vector")
                        if not isinstance(vec, list):
                            continue
                        v = [float(x) for x in vec]
                        n = float(c.get("norm") or 0.0)
                        out.append(_EmbeddedChunk(source=str(c.get("source") or ""), text=str(c.get("text") or ""), vector=v, norm=n))
                    if out:
                        return out
        except Exception:
            pass

        # Build fresh.
        chunks = _chunk_markdown_by_headings(md)
        filtered: List[_Chunk] = []
        for c in chunks:
            t = c.text.strip()
            # Skip chunks that are basically just a title/header
            if len(t) < 80:
                continue
            # Skip if only contains a single markdown heading line
            if "\n" not in t and t.lstrip().startswith("#"):
                continue
            filtered.append(c)

        embedded: List[_EmbeddedChunk] = []
        for c in filtered:
            vec = _embed_with_gemini(c.text, task_type="retrieval_document")
            n = math.sqrt(sum(x * x for x in vec))
            embedded.append(_EmbeddedChunk(source=c.source, text=c.text, vector=vec, norm=n))

        # Ensure cache directory exists
        try:
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "cache_key": cache_key,
                "model": model_name,
                "chunks": [
                    {"source": c.source, "text": c.text, "vector": c.vector, "norm": c.norm}
                    for c in embedded
                ],
            }
            self._cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        except Exception:
            # Cache failures shouldn't break the tool
            pass

        return embedded

    def _run(self, symptom: str, model: Optional[str] = None, top_k: int = 3) -> str:
        if not self._knowledge_path.exists():
            return (
                "Không tìm thấy file tài liệu kỹ thuật nội bộ. "
                f"Expected at: {self._knowledge_path}"
            )

        md = self._knowledge_path.read_text(encoding="utf-8", errors="ignore")
        query = " ".join([symptom or "", model or ""]).strip()

        best: List[_Chunk] = []
        # Prefer semantic search if configured; fallback to keyword search.
        try:
            embedded_chunks = self._load_or_build_index(md)
            q_vec = _embed_with_gemini(query, task_type="retrieval_query")
            q_norm = math.sqrt(sum(x * x for x in q_vec))
            scored2: List[tuple[float, _EmbeddedChunk]] = []
            for c in embedded_chunks:
                sim = _cosine(q_vec, q_norm, c.vector, c.norm)
                scored2.append((sim, c))
            scored2.sort(key=lambda x: x[0], reverse=True)
            # Avoid overly generic sections unless there are no alternatives.
            generic_prefixes = (
                "Kỹ thuật chẩn đoán & sửa máy sấy tóc",
                "An toàn bắt buộc",
                "Cấu phần thường gặp",
            )
            non_generic = [
                _Chunk(source=c.source, text=c.text)
                for _, c in scored2
                if c.source and not c.source.startswith(generic_prefixes)
            ]
            if len(non_generic) >= top_k:
                best = non_generic[:top_k]
            else:
                # Fill with best overall if needed
                best = non_generic
                for _, c in scored2:
                    chunk = _Chunk(source=c.source, text=c.text)
                    if chunk in best:
                        continue
                    best.append(chunk)
                    if len(best) >= top_k:
                        break
        except Exception:
            chunks = _chunk_markdown_by_headings(md)
            qn = _normalize(query)
            terms = [t for t in qn.split(" ") if len(t) >= 2]
            scored = []
            for c in chunks:
                tn = _normalize(c.text)
                s = _score_chunk(terms, tn)
                if s > 0:
                    scored.append((s, c))
            scored.sort(key=lambda x: x[0], reverse=True)
            best = [c for _, c in scored[:top_k]]

        if not best:
            return (
                "Không tìm thấy đoạn phù hợp trong tài liệu kỹ thuật cho triệu chứng này.\n"
                "Gợi ý: thử mô tả triệu chứng rõ hơn (ví dụ: 'có gió nhưng không nóng', 'tự ngắt sau 2 phút', 'mùi khét')."
            )

        # Tool output is plaintext but structured to be easy for the agent to cite.
        out_lines = ["Kết quả tra cứu (tài liệu nội bộ):"]
        for i, c in enumerate(best, 1):
            excerpt = c.text.strip()
            if len(excerpt) > 700:
                excerpt = excerpt[:700].rstrip() + "\n...(truncated)"
            out_lines.append(f"\n[{i}] SOURCE: {c.source}\n{excerpt}")

        return "\n".join(out_lines).strip()


class CatalogLookupInput(BaseModel):
    query: str = Field(..., description="Model/brand/từ khóa sản phẩm máy sấy tóc cần tìm trong catalog.")
    top_k: int = Field(5, ge=1, le=10, description="Số dòng/khối phù hợp muốn trả về.")


class CatalogLookupTool(BaseTool):
    name: str = "hair_dryer_catalog_lookup"
    description: str = (
        "Tra cứu catalog nội bộ máy sấy tóc (model/brand/watt/features). "
        "Dùng để nhận diện model và thông tin sản phẩm trước khi tư vấn."
    )
    args_schema: Type[BaseModel] = CatalogLookupInput

    def __init__(self, catalog_path: Optional[Path] = None):
        super().__init__()
        self._catalog_path = catalog_path or (_repo_root_from_this_file() / "knowledge" / "catalog.txt")

    def _run(self, query: str, top_k: int = 5) -> str:
        if not self._catalog_path.exists():
            return f"Không tìm thấy catalog nội bộ. Expected at: {self._catalog_path}"

        raw = self._catalog_path.read_text(encoding="utf-8", errors="ignore")
        qn = _normalize(query)
        terms = [t for t in qn.split(" ") if len(t) >= 2]

        # Simple block splitting: entries separated by blank line.
        # Keep only product blocks to avoid returning file headers/comments.
        blocks = [b.strip() for b in raw.split("\n\n") if b.strip().startswith("- model:")]
        scored = []
        for b in blocks:
            bn = _normalize(b)
            score = _score_chunk(terms, bn)
            if score > 0:
                scored.append((score, b))

        scored.sort(key=lambda x: x[0], reverse=True)
        best = [b for _, b in scored[:top_k]]

        if not best:
            return "Không tìm thấy sản phẩm phù hợp trong catalog."

        out_lines = ["Kết quả tra cứu catalog (nội bộ):"]
        for i, b in enumerate(best, 1):
            out_lines.append(f"\n[{i}]\n{b}")
        return "\n".join(out_lines).strip()

