"""Supabase product search tool for RAG-based product recommendations."""

from __future__ import annotations

import os
import re
import unicodedata
from typing import Type, List, Dict, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from supabase import create_client, Client


class SupabaseProductSearchInput(BaseModel):
    """Input schema for Supabase product search."""

    search_query: str = Field(
        ...,
        description=(
            "Từ khóa tìm sản phẩm trong database, ví dụ: 'máy sấy tóc', 'giá rẻ', "
            "'HD-1800ION'. Dùng '*' để xem toàn bộ sản phẩm."
        ),
    )


class SupabaseProductSearchTool(BaseTool):
    name: str = "search_products_supabase"
    description: str = (
        "Tìm sản phẩm trong Supabase database theo tên, mô tả, hoặc ID. "
        "Dùng khi cần tìm sản phẩm hiện có hoặc tư vấn cho khách hàng. "
        "Nếu muốn xem toàn bộ sản phẩm, dùng search_query='*'. "
        "Input phải là JSON object chỉ có key 'search_query' (string)."
    )
    args_schema: Type[BaseModel] = SupabaseProductSearchInput

    def __init__(self):
        super().__init__()
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """Lazy load Supabase client."""
        if self._client is None:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            
            if not url or not key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
            
            self._client = create_client(url, key)
        return self._client

    def _run(self, search_query: str) -> str:
        """Execute product search in Supabase."""
        try:
            query = search_query.strip()
            
            # Get all in-stock products
            if not query or query == "*":
                products = self._get_all_products()
                return self._format_results(
                    products,
                    heading="Toàn bộ sản phẩm hiện có trong kho:"
                )
            
            # Search products
            products = self._search_products(query)
            
            if products:
                return self._format_results(
                    products,
                    heading=f"Các sản phẩm phù hợp với từ khóa '{search_query}':"
                )
            
            # No results - show all available products
            all_products = self._get_all_products()
            product_names = [p.get("name", "N/A") for p in all_products]
            suggestions = "\n".join(f"- {name}" for name in product_names)
            
            return (
                f"Không tìm thấy sản phẩm khớp với từ khóa '{search_query}'.\n"
                "Các sản phẩm hiện có:\n"
                f"{suggestions}"
            )
            
        except Exception as e:
            return f"Lỗi khi tìm kiếm sản phẩm: {str(e)}"

    def _get_all_products(self) -> List[Dict]:
        """Get all in-stock products from Supabase."""
        response = self.client.table("products").select("*").eq("status", "in_stock").execute()
        return response.data or []

    def _search_products(self, query: str) -> List[Dict]:
        """Search products using normalized text matching."""
        all_products = self._get_all_products()
        
        if not all_products:
            return []
        
        # Normalize query
        normalized_query = self._normalize_text(query)
        query_terms = [
            term for term in re.split(r"[^a-zA-Z0-9]+", normalized_query)
            if len(term) >= 2
        ]
        
        if not query_terms:
            query_terms = [normalized_query]
        
        # Score each product
        scored_products: List[tuple[int, str, Dict]] = []
        
        for product in all_products:
            # Combine searchable fields
            searchable_text = " ".join([
                product.get("id", ""),
                product.get("name", ""),
                product.get("description", ""),
                product.get("specifications", ""),
                str(product.get("price", "")),
            ])
            
            normalized_product = self._normalize_text(searchable_text)
            
            # Calculate score
            score = sum(normalized_product.count(term) for term in query_terms)
            
            # Bonus for exact phrase match
            if normalized_query in normalized_product:
                score += 5
            
            # Bonus for ID match
            if normalized_query in self._normalize_text(product.get("id", "")):
                score += 10
            
            if score > 0:
                scored_products.append((score, product.get("id", ""), product))
        
        # Sort by score (desc), then by ID
        scored_products.sort(key=lambda item: (-item[0], item[1]))
        
        # Return top 5
        return [product for _, _, product in scored_products[:5]]

    def _normalize_text(self, text: str) -> str:
        """Normalize text for search (remove accents, lowercase)."""
        text = unicodedata.normalize("NFKD", text)
        text = "".join(char for char in text if not unicodedata.combining(char))
        return text.casefold()

    def _format_results(self, products: List[Dict], heading: str) -> str:
        """Format product results for display."""
        if not products:
            return heading + "\n\nKhông có sản phẩm nào."
        
        formatted_products = []
        
        for product in products:
            product_info = [
                f"[ID: {product.get('id', 'N/A')}]",
                f"Tên: {product.get('name', 'N/A')}",
                f"Giá: {self._format_price(product.get('price'))}",
            ]
            
            if product.get("description"):
                product_info.append(f"Mô tả: {product.get('description')}")
            
            if product.get("specifications"):
                product_info.append(f"Thông số: {product.get('specifications')}")
            
            product_info.append(f"Trạng thái: {self._format_status(product.get('status'))}")
            
            formatted_products.append("\n".join(product_info))
        
        return heading + "\n\n" + "\n\n---\n\n".join(formatted_products)

    def _format_price(self, price) -> str:
        """Format price for display."""
        if price is None:
            return "N/A"
        try:
            return f"{int(price):,}đ".replace(",", ".")
        except (ValueError, TypeError):
            return str(price)

    def _format_status(self, status: str) -> str:
        """Format status for display."""
        status_map = {
            "in_stock": "Còn hàng",
            "out_of_stock": "Hết hàng"
        }
        return status_map.get(status, status)


# Global instance
_SUPABASE_PRODUCT_SEARCH_TOOL: Optional[SupabaseProductSearchTool] = None


def build_supabase_product_search_tool() -> SupabaseProductSearchTool:
    """Get or create global Supabase product search tool instance."""
    global _SUPABASE_PRODUCT_SEARCH_TOOL
    
    if _SUPABASE_PRODUCT_SEARCH_TOOL is None:
        _SUPABASE_PRODUCT_SEARCH_TOOL = SupabaseProductSearchTool()
    
    return _SUPABASE_PRODUCT_SEARCH_TOOL
