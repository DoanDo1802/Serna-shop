#!/usr/bin/env python
"""FastAPI server for agent chat with n8n integration."""

import json
import warnings
import yaml
import os
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agent_sale.crew import AgentSale
from agent_sale.session_manager import get_session_manager
from agent_sale.message_batcher import MessageBatcher
from agent_sale.tools.email_handoff_tool import EmailHandoffTool
from agent_sale.tools.hair_dryer_troubleshooting import (
    HairDryerTroubleshootingLookupTool,
    CatalogLookupTool,
)
from agent_sale.tools.supabase_product_search_tool import SupabaseProductSearchTool

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Agent Sale API",
    description="Chat API for IonQ hair dryer sales agent with n8n integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
session_manager = get_session_manager()
user_crews: Dict[str, any] = {}
user_batchers: Dict[str, Dict] = {}  # Message batcher + results per user


# Request/Response models
class MessageData(BaseModel):
    """Message data from n8n."""
    text: Optional[str] = None
    sender: str
    conversation_short_id: Optional[str] = None
    conversation_id: Optional[str] = None
    create_time: Optional[str] = None
    message_type: str = "text"
    base64Image: Optional[str] = None


class WebhookEvent(BaseModel):
    """Webhook event from n8n."""
    event: str
    data: MessageData


class ChatRequest(BaseModel):
    """Chat request (can be single event or array)."""
    events: Optional[List[WebhookEvent]] = None
    # Also support direct fields
    event: Optional[str] = None
    data: Optional[MessageData] = None


class ChatResponse(BaseModel):
    """Chat response matching n8n format."""
    event: str
    data: Dict


def _clean_agent_reasoning(text: str) -> str:
    """
    Remove agent internal reasoning (Thought, Action, Observation).
    Extract only the final answer or clean response.
    """
    import re
    
    # If text contains "Thought:" or "Action:", extract only after "Observation:" or clean it
    if "Thought:" in text or "Action:" in text:
        # Try to extract observation (tool result)
        obs_match = re.search(r'Observation:\s*(.+?)(?:\n\n|$)', text, re.DOTALL)
        if obs_match:
            observation = obs_match.group(1).strip()
            # If observation is "Đã gửi handoff email", convert to user-friendly message
            if "Đã gửi handoff email" in observation or "handoff email" in observation.lower():
                return "Dạ mình đã ghi nhận thông tin, CSKH sẽ liên hệ lại sớm nhất nhé!"
            return observation
        
        # If no observation, try to extract the intent and create response
        if "handoff" in text.lower() and ("customer_name" in text or "customer_phone" in text):
            return "Dạ mình đã ghi nhận thông tin, CSKH sẽ liên hệ lại sớm nhất nhé!"
        
        # Otherwise return a generic message
        return "Dạ mình đã nhận được yêu cầu của bạn. Bạn cần hỗ trợ thêm gì không ạ?"
    
    return text


def _clean_markdown_for_chat(text: str) -> str:
    """
    Clean markdown formatting for chat platforms.
    Remove ** (bold), __ (italic), - (list), etc.
    Add proper line breaks.
    """
    import re
    
    # Remove bold markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    
    # Remove italic markers
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # Convert markdown lists to plain text with line breaks
    text = re.sub(r'^\s*[-*]\s+', '• ', text, flags=re.MULTILINE)
    
    # Convert numbered lists
    text = re.sub(r'^\s*\d+\.\s+', '• ', text, flags=re.MULTILINE)
    
    # Remove code blocks
    text = re.sub(r'```[a-z]*\n?', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Clean up multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Ensure proper line breaks (but not too many)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def _try_parse_json_object(text: str) -> dict | None:
    try:
        obj = json.loads(text)
    except Exception:
        return None
    return obj if isinstance(obj, dict) else None


def _is_product_search_tool_args(obj: dict) -> bool:
    """Check if object is Supabase product search tool args."""
    return isinstance(obj.get("search_query"), str)


def _is_troubleshooting_tool_args(obj: dict) -> bool:
    return (
        isinstance(obj.get("symptom"), str)
        and ("model" not in obj or obj.get("model") is None or isinstance(obj.get("model"), str))
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


def process_message(user_id: str, message: str, message_type: str = "text") -> str:
    """Process a message for a specific user."""
    # Get or create session
    session = session_manager.get_or_create_session(user_id)
    
    # Get or create crew for this user
    if user_id not in user_crews:
        user_crews[user_id] = AgentSale().crew()
        print(f"[API] Created crew instance for user: {user_id}")
    
    crew = user_crews[user_id]
    
    # Handle image messages
    if message_type == "image":
        message = "Khách gửi hình ảnh (chưa hỗ trợ xử lý ảnh, vui lòng mô tả bằng text)"
    
    # Add user message to session
    session.add_message("user", message)
    conversation_history = session.get_history()
    
    # Format conversation context (last 10 messages)
    recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
    context_lines = []
    for msg in recent_history:
        role_label = "Khách" if msg["role"] == "user" else "Litte Q"
        context_lines.append(f"{role_label}: {msg['content']}")
    
    conversation_context = "\n".join(context_lines) if context_lines else "(Chưa có lịch sử)"
    
    # Check if user provided name + phone
    name, phone = _extract_name_phone(message)
    should_force_handoff = name and phone and len(conversation_history) > 2
    
    inputs = {
        "topic": message,
        "conversation_context": conversation_context,
        "current_year": str(datetime.now().year),
    }
    
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
                
                session.add_message("assistant", result_text)
            
            # Handle product search tool args (Supabase)
            elif obj and _is_product_search_tool_args(obj):
                search_query = obj.get("search_query", "")
                tool_out = SupabaseProductSearchTool()._run(search_query=search_query)
                
                if "Không tìm thấy" in tool_out:
                    result_text = "Dạ, mình chưa tìm thấy sản phẩm phù hợp. Bạn có thể cho mình biết rõ hơn về nhu cầu của bạn không ạ?"
                else:
                    # Extract product info from tool output
                    result_text = "Dạ, mình tìm thấy một số sản phẩm phù hợp. Bạn quan tâm đến sản phẩm nào ạ?"
                
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
                if should_force_handoff:
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
                
                session.add_message("assistant", result_text)
            
            else:
                session.add_message("assistant", result_text)
            
            # Clean agent reasoning (Thought/Action/Observation)
            result_text = _clean_agent_reasoning(result_text)
            
            # Clean markdown formatting for chat platforms
            result_text = _clean_markdown_for_chat(result_text)
            
            return result_text
            
    except Exception as e:
        # Remove last user message on error
        if session.get_history() and session.get_history()[-1]["role"] == "user":
            session.get_history().pop()
        error_msg = f"Xin lỗi, có lỗi xảy ra: {e}"
        return error_msg


@app.post("/chat", response_model=ChatResponse)
async def chat(request: List[WebhookEvent] | WebhookEvent):
    """
    Handle chat messages from n8n webhook.
    
    Accepts both formats:
    1. Array: [{"event": "message", "data": {...}}]
    2. Single: {"event": "message", "data": {...}}
    """
    try:
        # Handle array format
        if isinstance(request, list):
            if not request:
                raise HTTPException(status_code=400, detail="Empty array")
            event = request[0]
        # Handle single format
        else:
            event = request
        
        if event.event != "message":
            raise HTTPException(status_code=400, detail=f"Unsupported event type: {event.event}")
        
        data = event.data
        user_id = data.sender
        message = data.text or ""
        message_type = data.message_type
        
        # Process message
        response_text = process_message(user_id, message, message_type)
        
        # Return response in same format as input
        return ChatResponse(
            event="message",
            data={
                "text": response_text,
                "sender": "agent",
                "recipient": user_id,
                "conversation_short_id": data.conversation_short_id,
                "conversation_id": data.conversation_id,
                "create_time": str(int(datetime.now().timestamp() * 1000)),
                "message_type": "text"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/simple")
async def chat_simple(data: MessageData):
    """
    Simplified chat endpoint for n8n with message batching.
    Waits for batching to complete (30s debounce) then returns actual response.
    
    Example:
    {
      "text": "Xin chào",
      "sender": "6901461877361017858",
      "message_type": "text"
    }
    """
    import asyncio
    
    try:
        user_id = data.sender
        message = data.text or ""
        message_type = data.message_type
        
        # Get or create batcher for this user
        if user_id not in user_batchers:
            # Store result in a dict that can be accessed by callback
            user_results = {}
            
            def create_process_callback(uid: str):
                def callback(combined_message: str) -> str:
                    try:
                        print(f"[API] Processing message for user {uid}: {combined_message[:50]}...")
                        result = process_message(uid, combined_message, message_type)
                        user_results[uid] = result
                        print(f"[API] Stored result for user {uid}: {result[:50]}...")
                        return result
                    except Exception as e:
                        # Log chi tiết lỗi ở backend để debug
                        print(f"[API] ❌ Error processing message for user {uid}: {e}")
                        import traceback
                        traceback.print_exc()
                        
                        # User chỉ nhận message lịch sự
                        error_msg = "Xin lỗi, hệ thống đang bận. Vui lòng thử lại sau."
                        user_results[uid] = error_msg
                        return error_msg
                return callback
            
            user_batchers[user_id] = {
                'batcher': MessageBatcher(
                    process_callback=create_process_callback(user_id),
                    debounce_seconds=15.0,
                    max_wait_seconds=45.0,
                ),
                'results': user_results
            }
            print(f"[API] Created message batcher for user: {user_id}")
        
        batcher_data = user_batchers[user_id]
        batcher = batcher_data['batcher']
        results = batcher_data['results']
        
        # Add message to batcher
        batcher.add_message(message)
        
        # Wait for processing to complete (check every 0.5s, max 70s)
        # Note: Batcher debounce (15s) + Agent processing (up to 45s) + buffer (10s)
        max_wait = 120  # Enough time for debounce + processing
        waited = 0
        print(f"[API] Waiting for result for user {user_id}...")
        while user_id not in results and waited < max_wait:
            await asyncio.sleep(0.5)
            waited += 0.5
        
        # Get result
        if user_id in results:
            response_text = results.pop(user_id)  # Remove after getting
            print(f"[API] Got result for user {user_id}: {response_text[:50]}...")
        else:
            print(f"[API] Timeout waiting for result for user {user_id} after {waited}s")
            response_text = "Xin lỗi, hệ thống đang bận. Vui lòng thử lại sau."
        
        # Return response
        return {
            "text": response_text,
            "sender": "agent",
            "recipient": user_id,
            "conversation_short_id": data.conversation_short_id,
            "conversation_id": data.conversation_id,
            "create_time": str(int(datetime.now().timestamp() * 1000)),
            "message_type": "text"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/simple/immediate")
async def chat_simple_immediate(data: MessageData):
    """
    Immediate response without batching - for testing or urgent messages.
    
    Example:
    {
      "text": "Xin chào",
      "sender": "6901461877361017858",
      "message_type": "text"
    }
    """
    try:
        user_id = data.sender
        message = data.text or ""
        message_type = data.message_type
        
        # Process message immediately
        response_text = process_message(user_id, message, message_type)
        
        # Return response
        return {
            "text": response_text,
            "sender": "agent",
            "recipient": user_id,
            "conversation_short_id": data.conversation_short_id,
            "conversation_id": data.conversation_id,
            "create_time": str(int(datetime.now().timestamp() * 1000)),
            "message_type": "text"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{sender}")
async def get_history(sender: str, limit: int = 50):
    """Get conversation history for a sender."""
    try:
        session = session_manager.get_or_create_session(sender)
        history = session.get_history()
        
        # Limit results
        if limit:
            history = history[-limit:]
        
        return {
            "sender": sender,
            "message_count": len(history),
            "messages": history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    try:
        stats = session_manager.get_session_stats()
        return {
            "total_sessions": stats["total_sessions"],
            "total_messages": stats["total_messages"],
            "avg_messages_per_session": stats["avg_messages_per_session"],
            "active_users": stats["session_ids"],
            "crews_loaded": len(user_crews)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "agent-sale-api"}


# ============= CONFIG MANAGEMENT ENDPOINTS =============

# Config file paths
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
AGENTS_FILE = os.path.join(CONFIG_DIR, 'agents.yaml')
TASKS_FILE = os.path.join(CONFIG_DIR, 'tasks.yaml')


class AgentConfig(BaseModel):
    """Agent configuration model."""
    role: str
    goal: str
    backstory: str
    memory: bool = False
    max_iter: int = 10


class TaskConfig(BaseModel):
    """Task configuration model."""
    description: str
    expected_output: str
    agent: str


@app.get("/config/agents")
async def get_agents_config():
    """Get all agents configuration."""
    try:
        with open(AGENTS_FILE, 'r', encoding='utf-8') as f:
            agents = yaml.safe_load(f) or {}
        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading agents config: {str(e)}")


@app.get("/config/tasks")
async def get_tasks_config():
    """Get all tasks configuration."""
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            tasks = yaml.safe_load(f) or {}
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading tasks config: {str(e)}")


@app.put("/config/agents/{agent_name}")
async def update_agent_config(agent_name: str, config: AgentConfig):
    """Update a specific agent configuration."""
    try:
        # Read current config
        with open(AGENTS_FILE, 'r', encoding='utf-8') as f:
            agents = yaml.safe_load(f) or {}
        
        # Update agent
        agents[agent_name] = config.dict()
        
        # Write back
        with open(AGENTS_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(agents, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        return {"message": f"Agent '{agent_name}' updated successfully", "agent": agents[agent_name]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating agent config: {str(e)}")


@app.put("/config/tasks/{task_name}")
async def update_task_config(task_name: str, config: TaskConfig):
    """Update a specific task configuration."""
    try:
        # Read current config
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            tasks = yaml.safe_load(f) or {}
        
        # Update task
        tasks[task_name] = config.dict()
        
        # Write back
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(tasks, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        return {"message": f"Task '{task_name}' updated successfully", "task": tasks[task_name]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task config: {str(e)}")


@app.post("/config/reload")
async def reload_config():
    """Reload agent configuration (clear crews to force reload on next message)."""
    try:
        global user_crews
        user_crews.clear()
        return {"message": "Configuration reloaded. All crews will be recreated on next message."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading config: {str(e)}")


@app.post("/config/test")
async def test_config():
    """Test current configuration by creating a new crew instance."""
    try:
        # Create a test crew to verify config loads correctly
        test_crew = AgentSale()
        
        # Get agent and task info
        agents_info = []
        for agent in test_crew.agents:
            agents_info.append({
                "role": agent.role,
                "goal": agent.goal[:100] + "..." if len(agent.goal) > 100 else agent.goal,
            })
        
        tasks_info = []
        for task in test_crew.tasks:
            tasks_info.append({
                "description": task.description[:100] + "..." if len(task.description) > 100 else task.description,
            })
        
        return {
            "message": "Configuration loaded successfully",
            "agents": agents_info,
            "tasks": tasks_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing config: {str(e)}")


# ==================== KNOWLEDGE FILE ENDPOINTS ====================

@app.get("/knowledge/files")
async def get_knowledge_files():
    """Get list of all knowledge files."""
    try:
        knowledge_dir = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge")
        
        if not os.path.exists(knowledge_dir):
            return {"files": []}
        
        files = [f for f in os.listdir(knowledge_dir) if f.endswith(('.md', '.txt'))]
        files.sort()
        
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing knowledge files: {str(e)}")


@app.get("/knowledge/files/{filename}")
async def get_knowledge_file(filename: str):
    """Get content of a specific knowledge file."""
    try:
        knowledge_dir = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge")
        file_path = os.path.join(knowledge_dir, filename)
        
        # Security check: prevent directory traversal
        if not os.path.abspath(file_path).startswith(os.path.abspath(knowledge_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {"filename": filename, "content": content}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading knowledge file: {str(e)}")


class KnowledgeFileContent(BaseModel):
    """Knowledge file content for update."""
    content: str


@app.put("/knowledge/files/{filename}")
async def update_knowledge_file(filename: str, data: KnowledgeFileContent):
    """Update content of a specific knowledge file."""
    try:
        knowledge_dir = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge")
        file_path = os.path.join(knowledge_dir, filename)
        
        # Security check: prevent directory traversal
        if not os.path.abspath(file_path).startswith(os.path.abspath(knowledge_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data.content)
        
        return {"message": f"File '{filename}' updated successfully", "filename": filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating knowledge file: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Get port from command line or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    
    print(f"Starting API server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
