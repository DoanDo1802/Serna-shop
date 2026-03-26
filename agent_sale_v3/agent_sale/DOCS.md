# Agent Sale - Documentation

## Tổng quan

Agent AI tư vấn và bán máy sấy tóc IonQ với các tính năng:
- Tìm kiếm sản phẩm từ Supabase database
- Tra cứu lỗi kỹ thuật
- Chuyển tiếp cho CSKH qua email
- Message batching (gom tin nhắn)
- Multi-user session management
- Persistent memory với Supabase

## Cấu trúc dự án

```
agent_sale/
├── src/agent_sale/
│   ├── config/
│   │   ├── agents.yaml      # Cấu hình agent
│   │   └── tasks.yaml       # Cấu hình tasks
│   ├── tools/
│   │   ├── supabase_product_search_tool.py  # Tìm sản phẩm
│   │   ├── hair_dryer_troubleshooting.py    # Tra lỗi kỹ thuật
│   │   └── email_handoff_tool.py            # Handoff CSKH
│   ├── api.py               # FastAPI endpoints
│   ├── crew.py              # CrewAI setup
│   ├── main.py              # CLI interface
│   ├── message_batcher.py   # Message batching
│   ├── session_manager.py   # Session management
│   └── supabase_storage.py  # Supabase integration
├── knowledge/
│   ├── catalog.txt          # Catalog cũ (reference)
│   └── hair_dryer_troubleshooting.md
├── .env                     # Environment variables
└── pyproject.toml          # Dependencies
```

## Setup

### 1. Environment Variables

Tạo file `.env`:

```bash
# LLM Configuration
MODEL=openai/cx/gpt-5.2
OPENAI_API_BASE=http://localhost:20128/v1
OPENAI_API_KEY=your_api_key

# Google API for embeddings
GOOGLE_API_KEY=your_google_api_key

# SMTP for email
SMTP_USER=your_email@gmail.com
SMTP_APP_PASSWORD=your_app_password

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key
```

### 2. Supabase Setup

Chạy SQL trong Supabase SQL Editor:

```sql
-- Xem file setup_supabase_tables.sql
```

### 3. Install Dependencies

```bash
cd agent_sale
uv sync
```

## Chạy ứng dụng

### API Server (Production)

```bash
cd agent_sale
uv run uvicorn src.agent_sale.api:app --host 0.0.0.0 --port 8000
```

### CLI Mode (Testing)

```bash
cd agent_sale
uv run python src/agent_sale/main.py
```

## API Endpoints

### POST /chat/simple

Endpoint chính cho n8n integration với message batching.

**Request:**
```json
{
  "text": "Xin chào",
  "sender": "user_id",
  "message_type": "text",
  "conversation_short_id": "123",
  "conversation_id": "456"
}
```

**Response:**
```json
{
  "text": "Dạ chào bạn...",
  "sender": "agent",
  "recipient": "user_id",
  "conversation_short_id": "123",
  "conversation_id": "456",
  "create_time": "1234567890",
  "message_type": "text"
}
```

**Timing:**
- Debounce: 15s (đợi sau tin nhắn cuối)
- Max wait: 45s (từ tin nhắn đầu)
- API timeout: 70s (đủ cho debounce + processing)

### POST /chat/simple/immediate

Xử lý ngay lập tức, không có batching.

### GET /history/{sender}

Lấy lịch sử hội thoại.

### GET /stats

Thống kê hệ thống.

## Tools

### 1. search_products_supabase

Tìm sản phẩm trong Supabase database.

**Input:**
```json
{"search_query": "máy sấy giá rẻ"}
```

**Khi nào dùng:**
- Khách hỏi về sản phẩm
- Khách hỏi giá
- Khách cần tư vấn

### 2. hair_dryer_troubleshooting_lookup

Tra cứu lỗi kỹ thuật.

**Input:**
```json
{
  "symptom": "máy tự ngắt",
  "model": "ionQ A1",
  "top_k": 1
}
```

**Khi nào dùng:**
- Khách báo lỗi
- Khách cần hướng dẫn sửa

### 3. handoff_support_via_email

Chuyển cho CSKH.

**Input:**
```json
{
  "customer_name": "Nguyễn Văn A",
  "customer_phone": "0912345678",
  "issue": "Yêu cầu bảo hành",
  "product_model": "ionQ A1"
}
```

**Khi nào dùng:**
- Khách yêu cầu đổi trả
- Khách yêu cầu bảo hành
- Vấn đề phức tạp

## Message Batching

Hệ thống tự động gom tin nhắn liên tiếp:

```
0s:   User: "Xin chào"
5s:   User: "Tìm máy sấy"
10s:  User: "Giá rẻ"
25s:  (15s sau tin cuối) → Xử lý: "Xin chào | Tìm máy sấy | Giá rẻ"
```

**Lợi ích:**
- Hiểu context tốt hơn
- Giảm số lần gọi LLM
- Trả lời mạch lạc hơn

## Multi-User Support

Mỗi user có:
- Session riêng (Supabase)
- Crew instance riêng
- Message batcher riêng
- Conversation history riêng

## Troubleshooting

### Agent có output nhưng n8n nhận "Hệ thống đang bận"

**Nguyên nhân:** Timeout - Agent xử lý lâu hơn max_wait

**Giải pháp:** Đã tăng max_wait lên 70s

**Check logs:**
```bash
grep "Error processing message" api.log
grep "Timeout waiting for result" api.log
```

### Tool execution error

**Nguyên nhân:** Agent trả về JSON sai format

**Giải pháp:** Check prompt trong `tasks.yaml`, đảm bảo có ví dụ rõ ràng

### Supabase connection error

**Nguyên nhân:** Thiếu env variables

**Giải pháp:** Check `.env` file có đầy đủ SUPABASE_URL và SUPABASE_KEY

## Monitoring

### Logs quan trọng

```bash
# Processing
[API] Processing message for user 123: ...
[API] Stored result for user 123: ...

# Errors
[API] ❌ Error processing message for user 123: ...

# Timeout
[API] Timeout waiting for result for user 123 after 70s
```

### Stats endpoint

```bash
curl http://localhost:8000/stats
```

## Migration Notes

### Catalog.txt → Supabase

- ✅ Đã migrate từ file sang database
- ✅ Tool mới: `SupabaseProductSearchTool`
- ✅ API đã cập nhật xử lý tool mới
- 📝 File `catalog.txt` giữ lại để reference

### Message Batching

- ✅ Debounce: 30s → 15s (nhanh hơn)
- ✅ Max wait: 60s → 45s
- ✅ API timeout: 65s → 70s

## Best Practices

1. **Luôn test với CLI trước khi deploy API**
2. **Monitor logs để phát hiện lỗi sớm**
3. **Backup Supabase data định kỳ**
4. **Update prompt khi thêm tool mới**
5. **Test message batching với nhiều tin nhắn**

## Support

Xem thêm tài liệu:
- `MEMORY_EXPLAINED.md` - Chi tiết về memory system
- `MESSAGE_BATCHING.md` - Chi tiết về message batching
- `MULTI_USER_GUIDE.md` - Hướng dẫn multi-user
- `NGROK_SETUP.md` - Setup ngrok cho testing
- `SUPABASE_RAG_MIGRATION.md` - Chi tiết migration
- `FIX_API_TOOL_MISMATCH.md` - Fix tool mismatch issue
- `FIX_MISSING_MESSAGES.md` - Fix missing messages issue
- `TOOLS_GUIDE.md` - Hướng dẫn chi tiết về tools
