#!/usr/bin/env python3
"""Test single tool call to debug why agent doesn't use tools."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agent_sale.crew import AgentSale

def test_simple_product_query():
    """Test with the simplest possible product query."""
    print("="*80)
    print("TEST: Simple Product Query - 'Có sản phẩm j?'")
    print("="*80)
    print()
    print("Expected: Agent should call search_products_supabase tool")
    print("Looking for: 'Action: search_products_supabase' in output")
    print()
    print("-"*80)
    
    crew = AgentSale().crew()
    
    inputs = {
        "topic": "Có sản phẩm j?",
        "conversation_context": "Khách: Có sản phẩm j?"
    }
    
    print("\n🚀 Starting crew execution with verbose=2...\n")
    result = crew.kickoff(inputs=inputs)
    
    print("\n" + "="*80)
    print("FINAL RESULT:")
    print("="*80)
    if hasattr(result, 'raw'):
        print(result.raw)
    else:
        print(result)
    print()

if __name__ == "__main__":
    test_simple_product_query()
