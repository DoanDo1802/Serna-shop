# Test Checklist - Agent Tool Usage Fix

## Pre-test Setup

- [ ] Đảm bảo `.env` có đầy đủ config:
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - `SMTP_USER`
  - `SMTP_APP_PASSWORD`
  - `OPENAI_API_KEY`
  - `OPENAI_API_BASE`

- [ ] Đảm bảo có sản phẩm trong Supabase table `products` với `status='in_stock'`

## Test Cases

### Test 1: Product Search - "Có sản phẩm j?"

**Input:**
```
Khách: Có sản phẩm j?
```

**Expected Behavior:**
- [ ] Agent gọi tool `search_products_supabase` với `{"search_query": "*"}`
- [ ] Agent nhận được danh sách sản phẩm từ Supabase
- [ ] Agent liệt kê sản phẩm thực tế (tên, giá, mô tả)
- [ ] Agent KHÔNG nói "hệ thống chưa hiển thị"

**Actual Result:**
```
[Paste agent response here]
```

---

### Test 2: Product Search - "Máy giá rẻ"

**Input:**
```
Khách: Có máy giá rẻ không?
```

**Expected Behavior:**
- [ ] Agent gọi tool `search_products_supabase` với search_query phù hợp
- [ ] Agent nhận được danh sách sản phẩm
- [ ] Agent gợi ý sản phẩm giá thấp

**Actual Result:**
```
[Paste agent response here]
```

---

### Test 3: Handoff - Full Flow

**Input 1:**
```
Khách: Gửi gmail quản lý
```

**Expected Behavior 1:**
- [ ] Agent hỏi: "Mình cho em xin Tên + SĐT..."
- [ ] Agent KHÔNG gọi tool ngay (vì chưa có thông tin)
- [ ] Agent KHÔNG nói "đã ghi nhận"

**Input 2:**
```
Khách: Đoàn 0123456789
```

**Expected Behavior 2:**
- [ ] Agent gọi tool `handoff_support_via_email` với:
  - `customer_name`: "Đoàn"
  - `customer_phone`: "0123456789"
  - `issue`: mô tả vấn đề
- [ ] Agent đợi Observation từ tool
- [ ] Agent thấy "Đã gửi handoff email tới..."
- [ ] SAU ĐÓ agent mới nói: "Dạ mình đã ghi nhận, CSKH sẽ liên hệ sớm"

**Actual Result:**
```
[Paste agent response here]
```

---

### Test 4: General Question (No Tool)

**Input:**
```
Khách: Máy ion có tốt không?
```

**Expected Behavior:**
- [ ] Agent trả lời trực tiếp (kiến thức chung)
- [ ] Agent KHÔNG gọi tool (vì không cần tra cứu thông tin cụ thể)

**Actual Result:**
```
[Paste agent response here]
```

---

## Debugging

Nếu test fail, check:

1. **Agent không gọi tool:**
   - [ ] Check verbose output trong log
   - [ ] Check tool có được load không (xem log khi start)
   - [ ] Check `max_iter` trong agents.yaml (phải >= 15)

2. **Agent gọi tool nhưng không đợi Observation:**
   - [ ] Check log xem có "Observation:" không
   - [ ] Có thể là LLM model issue - thử model khác

3. **Tool error:**
   - [ ] Check Supabase connection
   - [ ] Check SMTP credentials
   - [ ] Check tool implementation

## Success Criteria

✅ Pass nếu:
- Test 1: Agent gọi `search_products_supabase` và liệt kê sản phẩm thực
- Test 2: Agent gọi `search_products_supabase` với query phù hợp
- Test 3: Agent gọi `handoff_support_via_email` TRƯỚC KHI nói "đã ghi nhận"
- Test 4: Agent trả lời trực tiếp không gọi tool

❌ Fail nếu:
- Agent nói "hệ thống chưa hiển thị" khi hỏi về sản phẩm
- Agent nói "đã ghi nhận" mà không gọi handoff tool
- Agent bịa thông tin sản phẩm không có trong database
