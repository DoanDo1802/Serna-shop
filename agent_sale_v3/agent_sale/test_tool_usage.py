#!/usr/bin/env python3
"""Test script to verify agent tool usage."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agent_sale.crew import AgentSale


def test_product_search():
    """Test if agent calls search_products_supabase when asked about products."""
    print("\n" + "="*80)
    print("TEST 1: Product Search - 'Có sản phẩm j?'")
    print("="*80)
    
    crew = AgentSale().crew()
    
    inputs = {
        "topic": "Có sản phẩm j?",
        "conversation_context": "Khách: Ê\nLitte Q: Dạ em đây nè, mình cần tư vấn gì ạ?\nKhách: Có sản phẩm j?"
    }
    
    result = crew.kickoff(inputs=inputs)
    
    print("\n--- RESULT ---")
    print(result)
    print("\n--- EXPECTED ---")
    print("Agent should call search_products_supabase tool and list actual products from database")
    print("Agent should NOT say 'hệ thống chưa hiển thị'")
    

def test_handoff():
    """Test if agent calls handoff_support_via_email before saying 'đã ghi nhận'."""
    print("\n" + "="*80)
    print("TEST 2: Handoff - Customer provides name and phone")
    print("="*80)
    
    crew = AgentSale().crew()
    
    inputs = {
        "topic": "Đoàn 0123456789",
        "conversation_context": (
            "Khách: Gửi gmail quản lý\n"
            "Litte Q: Mình cho em xin Tên + SĐT nha\n"
            "Khách: Đoàn 0123456789"
        )
    }
    
    result = crew.kickoff(inputs=inputs)
    
    print("\n--- RESULT ---")
    print(result)
    print("\n--- EXPECTED ---")
    print("Agent should call handoff_support_via_email tool BEFORE saying 'đã ghi nhận'")
    print("Agent should NOT say 'đã ghi nhận' without calling the tool first")


if __name__ == "__main__":
    print("Testing Agent Tool Usage")
    print("Make sure you have .env configured with SUPABASE_URL, SUPABASE_KEY, etc.")
    
    # Test 1: Product search
    test_product_search()
    
    # Test 2: Handoff
    test_handoff()
    
    print("\n" + "="*80)
    print("Tests completed. Review the output above.")
    print("="*80)
