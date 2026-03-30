# Quick Fix Summary - Agent Tool Usage

## Vấn đề
Agent không gọi tool đúng cách:
1. Không gọi `search_products_supabase` khi khách hỏi "Có sản phẩm j?"
2. Nói "đã ghi nhận" TRƯỚC KHI gọi `handoff_support_via_email`

## Giải pháp

### 1. Cải thiện `config/tasks.yaml`
- ✅ Thêm phần "TRIGGER" rõ ràng cho mỗi tool
- ✅ Thêm ví dụ ĐÚNG và SAI
- ✅ Thêm quy trình từng bước cho HANDOFF
- ✅ Nhấn mạnh: KHÔNG nói "đã ghi nhận" nếu chưa gọi tool

### 2. Cải thiện `config/agents.yaml`
- ✅ Thêm "QUY TẮC TOOL USAGE" vào goal
- ✅ Tăng `max_iter` từ 10 → 15

### 3. Files đã sửa
- `agent_sale_v3/agent_sale/src/agent_sale/config/tasks.yaml`
- `agent_sale_v3/agent_sale/src/agent_sale/config/agents.yaml`
- `agent_sale_v3/agent_sale/src/agent_sale/crew.py` (revert system_template)

## Test
```bash
cd agent_sale_v3/agent_sale
python test_tool_usage.py
```

## Kỳ vọng
- Khách: "Có sản phẩm j?" → Agent gọi `search_products_supabase` → Liệt kê sản phẩm thực
- Khách: "Đoàn 0123456789" → Agent gọi `handoff_support_via_email` → Sau đó mới nói "đã ghi nhận"

## Xem chi tiết
Đọc `TOOL_USAGE_FIX.md` để biết thêm chi tiết và debug tips.
