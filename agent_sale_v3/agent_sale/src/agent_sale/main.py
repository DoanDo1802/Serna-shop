#!/usr/bin/env python
"""Main entry point with message batching and multi-user session support."""

import json
import sys
import warnings
import time
from datetime import datetime
from dotenv import load_dotenv

from agent_sale.crew import AgentSale
from agent_sale.tools.hair_dryer_troubleshooting import (
    HairDryerTroubleshootingLookupTool,
    CatalogLookupTool,
)
from agent_sale.tools.supabase_product_search_tool import SupabaseProductSearchTool
from agent_sale.tools.email_handoff_tool import EmailHandoffTool
from agent_sale.message_batcher import MessageBatcher
from agent_sale.session_manager import get_session_manager

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
load_dotenv()


def _try_parse_json_object(text: str) -> dict | None:
    try:
        obj = json.loads(text)
    except Exception:
        return None
    return obj if isinstance(obj, dict) else None


def _is_troubleshooting_tool_args(obj: dict) -> bool:
    return (
        isinstance(obj.get("symptom"), str)
        and ("model" not in obj or obj.get("model") is None or isinstance(obj.get("model"), str))
        and ("top_k" not in obj or isinstance(obj.get("top_k"), int))
    )


def _is_product_search_tool_args(obj: dict) -> bool:
    """Check if object is Supabase product search tool args."""
    return isinstance(obj.get("search_query"), str)


def _is_catalog_tool_args(obj: dict) -> bool:
    return (
        isinstance(obj.get("query"), str)
        and ("top_k" not in obj or isinstance(obj.get("top_k"), int))
    )


def _is_handoff_tool_args(obj: dict) -> bool:
    return (
        isinstance(obj.get("customer_name"), str)
        and isinstance(obj.get("customer_phone"), str)
        and isinstance(obj.get("issue"), str)
    )


def _extract_name_phone(text: str) -> tuple[str | None, str | None]:
    """Extract name and phone number from text."""
    import re
    
    phone_pattern = r'0\d{9,10}'
    phone_match = re.search(phone_pattern, text)
    phone = phone_match.group(0) if phone_match else None
    
    name = None
    if phone:
        before_phone = text[:text.index(phone)].strip()
        words = before_phone.split()
        if words:
            name = ' '.join(words[-min(4, len(words)):])
    
    return name, phone


def _detect_handoff_claim_without_tool(text: str) -> bool:
    """Detect if agent claims to have sent email but didn't actually call the tool."""
    handoff_keywords = [
        "đã ghi nhận thông tin",
        "đã chuyển CSKH",
        "đã chuyển thông tin",
        "đã chuyển sang",
        "bộ phận CSKH sẽ liên hệ",
        "chúng mình sẽ liên hệ lại",
        "đã gửi handoff",
        "mã ticket",
        "ticket",
        "sẽ liên hệ bạn trong",
    ]
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in handoff_keywords)


def run():
    """Run the crew with message batching and multi-user session support."""
    # Initialize session manager
    session_manager = get_session_manager()
    
    # Dictionary to store crew instance for each user
    user_crews = {}
    
    # Prompt for user_id (for CLI demo)
    print("=== Multi-User Session Support ===")
    user_id = input("Nhập user_id của bạn (Enter để tự động tạo): ").strip()
    if not user_id:
        import uuid
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        print(f"Đã tạo user_id: {user_id}")
    else:
        print(f"Sử dụng user_id: {user_id}")
    
    # Get or create session for this user
    session = session_manager.get_or_create_session(user_id)
    print(f"Session created at: {datetime.fromtimestamp(session.created_at).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create crew instance for this user
    if user_id not in user_crews:
        user_crews[user_id] = AgentSale().crew()
        print(f"Created crew instance for user: {user_id}")
    
    crew = user_crews[user_id]
    print()
    
    def process_message(combined_message: str) -> str:
        """Process a batched message through the crew."""
        # Add user message to session
        session.add_message("user", combined_message)
        conversation_history = session.get_history()
        
        # Format conversation context (last 10 messages)
        recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        context_lines = []
        for msg in recent_history:
            role_label = "Khách" if msg["role"] == "user" else "Litte Q"
            context_lines.append(f"{role_label}: {msg['content']}")
        
        conversation_context = "\n".join(context_lines) if context_lines else "(Chưa có lịch sử)"
        
        # Check if user provided name + phone
        name, phone = _extract_name_phone(combined_message)
        should_force_handoff = name and phone and len(conversation_history) > 2
        
        inputs = {
            "topic": combined_message,
            "conversation_context": conversation_context,
            "current_year": str(datetime.now().year),
        }
        
        print(f"[DEBUG] Conversation context:\n{conversation_context}\n")
        
        try:
            result = crew.kickoff(inputs=inputs)
            if result is not None:
                result_text = getattr(result, "raw", str(result)).strip()
                obj = _try_parse_json_object(result_text)
                
                # Handle handoff tool args
                if obj and _is_handoff_tool_args(obj):
                    customer_name = obj.get("customer_name", "")
                    customer_phone = obj.get("customer_phone", "")
                    issue = obj.get("issue", "")
                    product_model = obj.get("product_model")
                    chat_history_json = obj.get("chat_history_json") or json.dumps(conversation_history, ensure_ascii=False)
                    
                    tool_out = EmailHandoffTool()._run(
                        customer_name=customer_name,
                        customer_phone=customer_phone,
                        issue=issue,
                        product_model=product_model,
                        chat_history_json=chat_history_json,
                    )
                    
                    if "Đã gửi handoff email" in tool_out:
                        result_text = f"Dạ, mình đã ghi nhận thông tin của anh/chị {customer_name} (SĐT {customer_phone}). Bộ phận CSKH sẽ liên hệ lại sớm nhất nhé!"
                    else:
                        result_text = f"Dạ, mình đã ghi nhận thông tin của anh/chị {customer_name} (SĐT {customer_phone}). Chúng mình sẽ liên hệ lại sớm nhất nhé!"
                    
                    print(f"[DEBUG] Email tool result: {tool_out}")
                    session.add_message("assistant", result_text)
                
                # Handle product search tool args (Supabase)
                elif obj and _is_product_search_tool_args(obj):
                    search_query = obj.get("search_query", "")
                    tool_out = SupabaseProductSearchTool()._run(search_query=search_query)
                    
                    if "Không tìm thấy" in tool_out:
                        result_text = "Dạ, mình chưa tìm thấy sản phẩm phù hợp. Bạn có thể cho mình biết rõ hơn về nhu cầu của bạn không ạ?"
                    else:
                        result_text = "Dạ, mình tìm thấy một số sản phẩm phù hợp. Bạn quan tâm đến sản phẩm nào ạ?"
                    
                    session.add_message("assistant", result_text)
                
                # Handle catalog tool args (legacy)
                elif obj and _is_catalog_tool_args(obj):
                    query = obj.get("query", "")
                    top_k = int(obj.get("top_k") or 5)
                    tool_out = CatalogLookupTool()._run(query=query, top_k=top_k)
                    
                    if "Không tìm thấy" in tool_out:
                        result_text = "Dạ, mình chưa tìm thấy sản phẩm phù hợp trong hệ thống. Bạn có thể cho mình biết rõ hơn về model hoặc nhu cầu của bạn không ạ?"
                    else:
                        result_text = "Dạ, mình tìm thấy một số sản phẩm IonQ phù hợp. Bạn quan tâm đến công suất, giá cả hay tính năng cụ thể nào ạ?"
                    
                    session.add_message("assistant", result_text)
                
                # Handle troubleshooting tool args
                elif obj and _is_troubleshooting_tool_args(obj):
                    symptom = obj.get("symptom", "")
                    model = obj.get("model")
                    top_k = int(obj.get("top_k") or 1)
                    tool_out = HairDryerTroubleshootingLookupTool()._run(
                        symptom=symptom,
                        model=model,
                        top_k=top_k,
                    )
                    reply_lines = []
                    reply_lines.append("Dạ máy tự ngắt thường do máy bị quá nhiệt vì tắc gió/đường gió bẩn hoặc quạt yếu ạ.")
                    reply_lines.append("Mình giúp mình vệ sinh lưới lọc phía sau, đảm bảo thoáng gió và thử ổ cắm khác nhé; nếu vẫn tự tắt thì nên ngừng dùng để bảo hành cho an toàn.")
                    if not model:
                        reply_lines.append("Bạn cho mình xin model trên thân máy (hoặc ảnh tem) để mình hướng dẫn đúng hơn nha.")
                    result_text = " ".join(reply_lines).strip()
                    session.add_message("assistant", result_text)
                
                # Detect if agent claims handoff without actually calling tool
                elif _detect_handoff_claim_without_tool(result_text):
                    print(f"[WARNING] Agent claimed to handoff but didn't call tool!")
                    
                    if should_force_handoff:
                        print(f"[AUTO-HANDOFF] Forcing handoff with name={name}, phone={phone}")
                        
                        issue = "Khách hàng yêu cầu hỗ trợ"
                        if len(conversation_history) > 2:
                            recent = conversation_history[-3:]
                            issue = " | ".join([f"{m['role']}: {m['content'][:50]}" for m in recent])
                        
                        tool_out = EmailHandoffTool()._run(
                            customer_name=name,
                            customer_phone=phone,
                            issue=issue,
                            product_model=None,
                            chat_history_json=json.dumps(conversation_history, ensure_ascii=False),
                        )
                        
                        if "Đã gửi handoff email" in tool_out:
                            result_text = f"Dạ, mình đã ghi nhận thông tin của bạn {name} (SĐT {phone}). Bộ phận CSKH sẽ liên hệ lại sớm nhất nhé!"
                        else:
                            result_text = f"Dạ, mình đã ghi nhận thông tin của bạn {name} (SĐT {phone}). Chúng mình sẽ liên hệ lại sớm nhất nhé!"
                        
                        print(f"[DEBUG] Email tool result: {tool_out}")
                    
                    session.add_message("assistant", result_text)
                
                else:
                    session.add_message("assistant", result_text)
                
                print(f"Agent: {result_text}")
                return result_text
                
        except Exception as e:
            # Remove last user message on error
            if session.get_history() and session.get_history()[-1]["role"] == "user":
                session.get_history().pop()
            error_msg = f"Xin lỗi, có lỗi xảy ra: {e}"
            print(f"Error: {error_msg}")
            return error_msg
    
    # Create message batcher
    batcher = MessageBatcher(
        process_callback=process_message,
        debounce_seconds=15.0,  # Wait 15s after last message
        max_wait_seconds=45.0,  # Max 45s from first message
    )
    
    print("Chat test mode with message batching (15s debounce).")
    print("Type multiple messages quickly - they will be batched together.")
    print("Type /exit to quit, /flush to process immediately.")
    print()
    
    while True:
        try:
            user_input = input("Bạn: ").strip()
        except EOFError:
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in {"/exit", "exit", "quit"}:
            print("Flushing pending messages...")
            batcher.flush()
            time.sleep(2)  # Wait for processing
            break
        
        if user_input.lower() == "/flush":
            print("Forcing immediate processing...")
            batcher.flush()
            continue
        
        # Add message to batcher
        batcher.add_message(user_input)
    
    print("Đã thoát chat.")


if __name__ == "__main__":
    run()
