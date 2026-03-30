# Fix Agent Tool Usage Issues

## Vấn đề phát hiện

Từ log, agent có 2 vấn đề nghiêm trọng:

### 1. Không gọi `search_products_supabase` khi khách hỏi về sản phẩm
```
Khách: "Ok Có sản phẩm j"
Agent: "Hi mình ơi, hiện tại hệ thống bên em chưa hiển thị danh sách sản phẩm..."
```
❌ SAI - Agent phải gọi tool để lấy danh sách sản phẩm thực tế từ Supabase

### 2. Nói "đã ghi nhận" TRƯỚC KHI gọi `handoff_support_via_email`
```
Khách: "Đoàn 12344321"
Agent: "Dạ mình đã ghi nhận, CSKH sẽ liên hệ sớm ạ"
```
❌ SAI - Agent chưa gọi tool nhưng đã nói "đã ghi nhận"

## Các thay đổi đã thực hiện

### 1. Cải thiện `tasks.yaml`
- Thêm phần "TRIGGER" rõ ràng cho việc gọi `search_products_supabase`
- Thêm ví dụ ĐÚNG và SAI để agent hiểu rõ hơn
- Thêm quy trình từng bước cho HANDOFF
- Nhấn mạnh: KHÔNG BAO GIỜ nói "đã ghi nhận" nếu chưa thấy Observation từ tool

### 2. Cải thiện `agents.yaml`
- Thêm "QUY TẮC TOOL USAGE" vào phần goal
- Nhấn mạnh 3 quy tắc quan trọng nhất
- Tăng `max_iter` từ 10 lên 15 để agent có đủ bước suy nghĩ

### 3. Thêm `system_template` vào `crew.py`
- Thêm system message với CRITICAL RULES
- Nhấn mạnh việc phải gọi tool TRƯỚC KHI trả lời
- Cảnh báo không được bịa thông tin

## Cách test

### Test thủ công
```bash
cd agent_sale_v3/agent_sale
python test_tool_usage.py
```

### Test qua API
```bash
# Start API server
cd agent_sale_v3/agent_sale
uv run fastapi dev src/agent_sale/api.py --port 8001

# Test product search
curl -X POST http://localhost:8001/chat/simple \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "Có sản phẩm j?"
  }'

# Test handoff
curl -X POST http://localhost:8001/chat/simple \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "Gửi gmail quản lý"
  }'

# Then provide name and phone
curl -X POST http://localhost:8001/chat/simple \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "Đoàn 0123456789"
  }'
```

## Kỳ vọng sau khi fix

### Test 1: Product Search
```
Khách: "Có sản phẩm j?"
Agent: 
  → Action: search_products_supabase
  → Action Input: {"search_query": "*"}
  → Observation: [Danh sách sản phẩm từ Supabase]
  → Final Answer: "Dạ bên em có các dòng máy sấy IonQ sau: [liệt kê sản phẩm thực tế]"
```

### Test 2: Handoff
```
Khách: "Gửi gmail quản lý"
Agent: "Mình cho em xin Tên + SĐT nha"

Khách: "Đoàn 0123456789"
Agent:
  → Action: handoff_support_via_email
  → Action Input: {"customer_name": "Đoàn", "customer_phone": "0123456789", "issue": "..."}
  → Observation: "Đã gửi handoff email tới..."
  → Final Answer: "Dạ mình đã ghi nhận, CSKH sẽ liên hệ sớm ạ"
```

## Debug tips

### Nếu agent vẫn không gọi tool:

1. **Check verbose output**: Xem agent có nhận diện được tool không
   ```python
   # In crew.py, đảm bảo verbose=True
   return Agent(..., verbose=True)
   ```

2. **Check tool description**: Tool description phải rõ ràng
   ```python
   # In tool file
   description: str = "Tìm sản phẩm trong Supabase database..."
   ```

3. **Check LLM model**: Đảm bảo model đủ mạnh để hiểu instruction
   ```bash
   # Check .env
   MODEL=openai/cx/gpt-5.2
   OPENAI_API_BASE=http://localhost:20128/v1
   ```

4. **Check max_iter**: Nếu agent dừng sớm, tăng max_iter
   ```yaml
   # In agents.yaml
   max_iter: 15  # hoặc cao hơn
   ```

5. **Enable tracing**: Để debug chi tiết hơn
   ```python
   # In crew.py
   return Crew(..., verbose=True)
   
   # Hoặc set env
   export CREWAI_TRACING_ENABLED=true
   ```

### Nếu agent gọi tool nhưng không đợi Observation:

Đây là vấn đề với LLM - cần:
1. Nhấn mạnh trong instruction: "ĐỢI Observation từ tool"
2. Thêm ví dụ cụ thể về flow: Action → Observation → Final Answer
3. Cảnh báo rõ ràng: "KHÔNG được nói 'đã ghi nhận' nếu chưa thấy Observation"

## Monitoring

Khi chạy production, theo dõi:
- Số lần agent gọi tool vs không gọi tool khi cần
- Số lần agent nói "đã ghi nhận" mà không có log gửi email
- Response time (nếu quá chậm, có thể do agent suy nghĩ quá nhiều vòng)

## Rollback

Nếu cần rollback:
```bash
git diff HEAD agent_sale_v3/agent_sale/src/agent_sale/config/
git checkout HEAD -- agent_sale_v3/agent_sale/src/agent_sale/config/
```
