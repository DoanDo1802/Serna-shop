#!/usr/bin/env python3
"""Test script simulating 3 users with different conversation flows."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agent_sale.crew import AgentSale


def print_separator(title):
    """Print a nice separator."""
    print("\n" + "="*100)
    print(f"  {title}")
    print("="*100 + "\n")


def simulate_user_conversation(user_name, user_id, messages):
    """Simulate a conversation for one user."""
    print_separator(f"USER: {user_name} (ID: {user_id})")
    
    conversation_history = []
    
    for i, message in enumerate(messages, 1):
        print(f"\n--- Message {i}/3 ---")
        print(f"👤 {user_name}: {message}")
        print()
        
        # Build conversation context
        context_lines = []
        for entry in conversation_history:
            context_lines.append(f"Khách: {entry['user']}")
            context_lines.append(f"Litte Q: {entry['bot']}")
        context_lines.append(f"Khách: {message}")
        
        conversation_context = "\n".join(context_lines) if context_lines else f"Khách: {message}"
        
        # Create crew and run
        crew = AgentSale().crew()
        inputs = {
            "topic": message,
            "conversation_context": conversation_context
        }
        
        print("🤖 Litte Q đang suy nghĩ...")
        start_time = time.time()
        
        try:
            result = crew.kickoff(inputs=inputs)
            elapsed = time.time() - start_time
            
            # Extract final answer
            if hasattr(result, 'raw'):
                bot_response = str(result.raw)
            else:
                bot_response = str(result)
            
            print(f"\n🤖 Litte Q: {bot_response}")
            print(f"\n⏱️  Response time: {elapsed:.2f}s")
            
            # Save to history
            conversation_history.append({
                "user": message,
                "bot": bot_response
            })
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            break
        
        # Small delay between messages
        if i < len(messages):
            time.sleep(1)
    
    print(f"\n✅ Conversation completed for {user_name}")


def main():
    """Run test with 3 users."""
    print_separator("TEST: 3 Users - Product Inquiry & Complaint Scenarios")
    print("Testing agent tool usage with realistic conversations")
    print("Expected: Agent should call tools when appropriate")
    
    # User 1: Product inquiry - should trigger search_products_supabase
    user1_messages = [
        "Chào em",
        "Có sản phẩm j?",
        "Máy nào giá rẻ nhất?"
    ]
    
    # User 2: Product inquiry with specific needs
    user2_messages = [
        "Hi",
        "Tư vấn máy sấy tóc cho tóc dày",
        "Có máy nào tầm 500k không?"
    ]
    
    # User 3: Complaint/handoff - should trigger handoff_support_via_email
    user3_messages = [
        "Máy em mua bị hỏng rồi",
        "Gửi cho quản lý giúp em",
        "Nguyễn Văn A 0912345678"
    ]
    
    # Run tests
    try:
        simulate_user_conversation("User 1 - Hỏi sản phẩm", "user_001", user1_messages)
        time.sleep(2)
        
        simulate_user_conversation("User 2 - Tư vấn cụ thể", "user_002", user2_messages)
        time.sleep(2)
        
        simulate_user_conversation("User 3 - Khiếu nại", "user_003", user3_messages)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print_separator("TEST SUMMARY")
    print("✅ Expected behaviors:")
    print()
    print("User 1 - Message 2 'Có sản phẩm j?':")
    print("  → Should call: search_products_supabase")
    print("  → Should list: Actual products from Supabase")
    print()
    print("User 1 - Message 3 'Máy nào giá rẻ nhất?':")
    print("  → Should call: search_products_supabase")
    print("  → Should recommend: Cheapest product")
    print()
    print("User 2 - Message 2 'Tư vấn máy sấy tóc cho tóc dày':")
    print("  → Should call: search_products_supabase")
    print("  → Should recommend: Suitable products")
    print()
    print("User 2 - Message 3 'Có máy nào tầm 500k không?':")
    print("  → Should call: search_products_supabase")
    print("  → Should filter: Products around 500k")
    print()
    print("User 3 - Message 2 'Gửi cho quản lý giúp em':")
    print("  → Should ask: Tên + SĐT")
    print("  → Should NOT call tool yet")
    print()
    print("User 3 - Message 3 'Nguyễn Văn A 0912345678':")
    print("  → Should call: handoff_support_via_email")
    print("  → Should wait: For Observation")
    print("  → Should say: 'Dạ mình đã ghi nhận' AFTER tool returns")
    print()
    print("="*100)


if __name__ == "__main__":
    print("\n🚀 Starting 3-User Test Simulation")
    print("Make sure:")
    print("  1. .env is configured with SUPABASE_URL, SUPABASE_KEY")
    print("  2. Products exist in Supabase 'products' table")
    print("  3. SMTP credentials are set for email handoff")
    print()
    input("Press ENTER to start test...")
    
    main()
