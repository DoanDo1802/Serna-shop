"""Test concurrent users with tool usage."""

import asyncio
import httpx
import time
from datetime import datetime
from typing import List, Dict


API_URL = "http://localhost:8000/chat/simple"

# 3 users với 3 tin nhắn mỗi người
TEST_SCENARIOS = {
    "user_001": [
        "Xin chào, tôi muốn tìm máy sấy tóc",
        "Có máy nào giá rẻ không?",
        "Cho tôi xem ionQ A1"
    ],
    "user_002": [
        "Chào bạn",
        "Máy ionQ Clover có tốt không?",
        "Giá bao nhiêu vậy?"
    ],
    "user_003": [
        "Hi",
        "Tìm máy sấy có ion âm",
        "Dưới 500k có không?"
    ]
}


class TestResult:
    """Store test results for analysis."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.messages_sent = []
        self.responses_received = []
        self.timings = []
        self.errors = []
        self.tool_usage = []
    
    def add_message(self, message: str, response: str, duration: float, error: str = None):
        self.messages_sent.append(message)
        self.responses_received.append(response)
        self.timings.append(duration)
        if error:
            self.errors.append(error)
    
    def detect_tool_usage(self, response: str):
        """Detect if response indicates tool was used."""
        tool_indicators = [
            "ionQ A1",
            "ionQ Clover",
            "193.000đ",
            "915.000đ",
            "280.000đ",
            "ion âm",
            "Còn hàng",
            "sản phẩm phù hợp"
        ]
        
        for indicator in tool_indicators:
            if indicator in response:
                self.tool_usage.append({
                    'indicator': indicator,
                    'response': response[:100]
                })
                return True
        return False
    
    def print_summary(self):
        """Print test summary for this user."""
        print(f"\n{'='*80}")
        print(f"📊 Test Summary for {self.user_id}")
        print(f"{'='*80}")
        
        print(f"\n📨 Messages sent: {len(self.messages_sent)}")
        print(f"✅ Responses received: {len(self.responses_received)}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"🔧 Tool usage detected: {len(self.tool_usage)}")
        
        print(f"\n⏱️  Timing:")
        if self.timings:
            print(f"   - Average: {sum(self.timings)/len(self.timings):.2f}s")
            print(f"   - Min: {min(self.timings):.2f}s")
            print(f"   - Max: {max(self.timings):.2f}s")
            print(f"   - Total: {sum(self.timings):.2f}s")
        
        print(f"\n💬 Conversation:")
        for i, (msg, resp, timing) in enumerate(zip(self.messages_sent, self.responses_received, self.timings), 1):
            print(f"\n   [{i}] User ({timing:.1f}s): {msg}")
            print(f"       Agent: {resp[:150]}{'...' if len(resp) > 150 else ''}")
        
        if self.tool_usage:
            print(f"\n🔧 Tool Usage Details:")
            for i, tool in enumerate(self.tool_usage, 1):
                print(f"   [{i}] Detected: {tool['indicator']}")
                print(f"       Response: {tool['response']}...")
        
        if self.errors:
            print(f"\n❌ Errors:")
            for i, error in enumerate(self.errors, 1):
                print(f"   [{i}] {error}")


async def send_message(client: httpx.AsyncClient, user_id: str, message: str) -> Dict:
    """Send a single message to the API."""
    payload = {
        "text": message,
        "sender": user_id,
        "message_type": "text",
        "conversation_short_id": f"test_{user_id}",
        "conversation_id": f"0:1:{user_id}:test"
    }
    
    start_time = time.time()
    try:
        response = await client.post(API_URL, json=payload, timeout=80.0)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'response': data.get('text', ''),
                'duration': duration,
                'error': None
            }
        else:
            return {
                'success': False,
                'response': '',
                'duration': duration,
                'error': f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        duration = time.time() - start_time
        return {
            'success': False,
            'response': '',
            'duration': duration,
            'error': str(e)
        }


async def test_user_conversation(client: httpx.AsyncClient, user_id: str, messages: List[str]) -> TestResult:
    """Test a complete conversation for one user."""
    result = TestResult(user_id)
    
    print(f"\n🚀 Starting test for {user_id}")
    
    for i, message in enumerate(messages, 1):
        print(f"   [{i}/{len(messages)}] Sending: {message[:50]}...")
        
        response_data = await send_message(client, user_id, message)
        
        result.add_message(
            message=message,
            response=response_data['response'],
            duration=response_data['duration'],
            error=response_data['error']
        )
        
        if response_data['success']:
            print(f"   ✅ Received response in {response_data['duration']:.2f}s")
            result.detect_tool_usage(response_data['response'])
        else:
            print(f"   ❌ Error: {response_data['error']}")
        
        # Small delay between messages from same user
        await asyncio.sleep(1)
    
    print(f"✅ Completed test for {user_id}")
    return result


async def run_concurrent_test():
    """Run concurrent tests for all users."""
    print("\n" + "="*80)
    print("🧪 CONCURRENT USER TEST - 3 Users, 3 Messages Each")
    print("="*80)
    print(f"\n⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API URL: {API_URL}")
    print(f"👥 Users: {len(TEST_SCENARIOS)}")
    print(f"💬 Total messages: {sum(len(msgs) for msgs in TEST_SCENARIOS.values())}")
    
    start_time = time.time()
    
    async with httpx.AsyncClient() as client:
        # Run all user conversations concurrently
        tasks = [
            test_user_conversation(client, user_id, messages)
            for user_id, messages in TEST_SCENARIOS.items()
        ]
        
        results = await asyncio.gather(*tasks)
    
    total_duration = time.time() - start_time
    
    # Print individual results
    for result in results:
        result.print_summary()
    
    # Print overall summary
    print(f"\n{'='*80}")
    print("📈 OVERALL TEST SUMMARY")
    print(f"{'='*80}")
    
    total_messages = sum(len(r.messages_sent) for r in results)
    total_responses = sum(len(r.responses_received) for r in results)
    total_errors = sum(len(r.errors) for r in results)
    total_tool_usage = sum(len(r.tool_usage) for r in results)
    
    print(f"\n📊 Statistics:")
    print(f"   - Total messages sent: {total_messages}")
    print(f"   - Total responses received: {total_responses}")
    print(f"   - Success rate: {(total_responses/total_messages*100):.1f}%")
    print(f"   - Total errors: {total_errors}")
    print(f"   - Tool usage detected: {total_tool_usage}/{total_messages} messages")
    print(f"   - Tool usage rate: {(total_tool_usage/total_messages*100):.1f}%")
    
    print(f"\n⏱️  Performance:")
    print(f"   - Total test duration: {total_duration:.2f}s")
    print(f"   - Average per message: {total_duration/total_messages:.2f}s")
    
    all_timings = []
    for r in results:
        all_timings.extend(r.timings)
    
    if all_timings:
        print(f"   - Fastest response: {min(all_timings):.2f}s")
        print(f"   - Slowest response: {max(all_timings):.2f}s")
        print(f"   - Average response time: {sum(all_timings)/len(all_timings):.2f}s")
    
    # Check if all users got tool responses
    print(f"\n🔧 Tool Usage Analysis:")
    for result in results:
        tool_rate = len(result.tool_usage) / len(result.messages_sent) * 100 if result.messages_sent else 0
        print(f"   - {result.user_id}: {len(result.tool_usage)}/{len(result.messages_sent)} messages ({tool_rate:.0f}%)")
    
    # Final verdict
    print(f"\n{'='*80}")
    if total_errors == 0 and total_tool_usage > 0:
        print("✅ TEST PASSED - All users received responses with tool usage!")
    elif total_errors == 0:
        print("⚠️  TEST PARTIAL - All responses received but low tool usage")
    else:
        print(f"❌ TEST FAILED - {total_errors} errors occurred")
    print(f"{'='*80}\n")


async def test_api_health():
    """Check if API is running."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ API is running")
                return True
            else:
                print(f"❌ API returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("\n💡 Make sure API is running:")
        print("   cd agent_sale")
        print("   uv run uvicorn src.agent_sale.api:app --host 0.0.0.0 --port 8000")
        return False


async def main():
    """Main test function."""
    print("\n🔍 Checking API health...")
    
    if not await test_api_health():
        return
    
    print("\n⏳ Starting test in 3 seconds...")
    await asyncio.sleep(3)
    
    await run_concurrent_test()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
