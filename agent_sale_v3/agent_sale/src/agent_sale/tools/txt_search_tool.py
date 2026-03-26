from __future__ import annotations

from pathlib import Path
import re
import unicodedata
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class CatalogSearchToolInput(BaseModel):
    """Input schema for local catalog search."""

    search_query: str = Field(
        ...,
        description=(
            "Từ khóa tìm sản phẩm trong catalog, ví dụ: 'da khô', 'chống nắng', "
            "'SKN-002'. Dùng '*' để xem toàn bộ catalog."
        ),
    )


class CatalogSearchTool(BaseTool):
    name: str = "search_catalog"
    description: str = (
        "Tìm sản phẩm trong catalog local theo SKU, tên, nhu cầu da, lợi ích hoặc giá. "
        "Dùng khi cần xác thực sản phẩm hiện có. Nếu muốn xem toàn bộ catalog, dùng search_query='*'. "
        "Input phải là JSON object chỉ có key 'search_query' (string)."
    )
    args_schema: Type[BaseModel] = CatalogSearchToolInput

    def _run(self, search_query: str) -> str:
        catalog_text = _load_catalog_text()
        products = _parse_product_blocks(catalog_text)

        query = search_query.strip()
        if not query or query == "*":
            return _format_results(products, heading="Toàn bộ sản phẩm hiện có trong catalog:")

        ranked_products = _search_products(products, query)
        if ranked_products:
            return _format_results(
                ranked_products,
                heading=f"Các sản phẩm phù hợp nhất với từ khóa '{search_query}':",
            )

        product_names = [line for product in products for line in product.splitlines() if line.startswith("Tên:")]
        suggestions = "\n".join(f"- {name.replace('Tên:', '').strip()}" for name in product_names)
        return (
            f"Không tìm thấy sản phẩm khớp rõ với từ khóa '{search_query}'.\n"
            "Các sản phẩm hiện có trong catalog:\n"
            f"{suggestions}"
        )


_TXT_SEARCH_TOOL: CatalogSearchTool | None = None
_CATALOG_PATH = Path(__file__).resolve().parents[3] / "knowledge" / "catalog.txt"


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return text.casefold()


def _load_catalog_text() -> str:
    if not _CATALOG_PATH.exists():
        raise FileNotFoundError(f"Catalog file not found: {_CATALOG_PATH}")
    return _CATALOG_PATH.read_text(encoding="utf-8")


def _parse_product_blocks(catalog_text: str) -> list[str]:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", catalog_text) if "[SKU]" in block]
    return blocks


def _search_products(products: list[str], query: str) -> list[str]:
    normalized_query = _normalize_text(query)
    query_terms = [term for term in re.split(r"[^a-zA-Z0-9]+", normalized_query) if len(term) >= 2]
    if not query_terms:
        query_terms = [normalized_query]

    scored_products: list[tuple[int, int, str]] = []
    for product in products:
        normalized_product = _normalize_text(product)
        score = sum(normalized_product.count(term) for term in query_terms)
        if normalized_query in normalized_product:
            score += 3
        if score > 0:
            scored_products.append((score, len(product), product))

    scored_products.sort(key=lambda item: (-item[0], item[1]))
    return [product for _, _, product in scored_products[:5]]


def _format_results(products: list[str], heading: str) -> str:
    formatted_products = "\n\n".join(products)
    return f"{heading}\n\n{formatted_products}" if formatted_products else heading


def build_txt_search_tool() -> CatalogSearchTool:
    global _TXT_SEARCH_TOOL
    if _TXT_SEARCH_TOOL is None:
        _TXT_SEARCH_TOOL = CatalogSearchTool()
    return _TXT_SEARCH_TOOL
