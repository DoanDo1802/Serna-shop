# CRITICAL ISSUE: Agent Không Gọi Tools

## Vấn đề

Agent KHÔNG BAO GIỜ gọi tools mặc dù:
1. ✅ Tools được load đúng vào agent
2. ✅ LLM model hỗ trợ function calling (đã test trực tiếp)
3. ✅ Tool descriptions đã được cải thiện
4. ✅ Instructions trong tasks.yaml rất rõ ràng

## Bằng chứng

### Test 1: "Có sản phẩm j?"
```
Expected: Action: search_products_supabase
Actual: "Dạ em vừa tra cứu trên hệ thống thì hiện chưa thấy..."
```
❌ Agent HALLUCINATE rằng đã tra cứu, nhưng KHÔNG GỌI TOOL

### Test 2: LLM Function Calling Test
```python
# Test trực tiếp với LiteLLM
response = completion(model="openai/cx/gpt-5.2", tools=[...])
```
✅ Model GỌI FUNCTION thành công!

## Nguyên nhân có thể

### 1. CrewAI sử dụng ReAct Prompting thay vì Function Calling

CrewAI có thể đang dùng ReAct pattern (Thought → Action → Observation) thay vì native function calling của OpenAI.

**Kiểm tra:**
- Xem log có "Thought:", "Action:", "Observation:" không
- Nếu KHÔNG có → CrewAI không dùng ReAct
- Nếu CÓ nhưng không gọi tool → ReAct prompt không hiệu quả

### 2. Agent Config Thiếu

Có thể cần config thêm:
```python
Agent(
    ...,
    use_system_prompt=True,  # Force system prompt
    respect_context_window=True,
    # Hoặc các config khác
)
```

### 3. Task Config Conflict

Task description quá dài có thể làm agent confused. Cần:
- Rút gọn task description
- Chỉ giữ phần quan trọng nhất
- Đưa examples ra ngoài

### 4. LLM Model Issue với CrewAI

Model `cx/gpt-5.2` qua 9router có thể:
- Không tương thích 100% với CrewAI
- Cần format khác
- Cần thêm config đặc biệt

## Giải pháp đề xuất

### Giải pháp 1: Force ReAct Pattern

Nếu CrewAI dùng ReAct, cần format instruction theo ReAct:

```yaml
description: >
  You MUST use this format:
  
  Thought: I need to search for products
  Action: search_products_supabase
  Action Input: {"search_query": "*"}
  Observation: [wait for tool result]
  Thought: Now I can answer
  Final Answer: [your response]
```

### Giải pháp 2: Thử Model Khác

Test với model khác để xác định vấn đề:
```python
llm = LLM(model="gpt-4")  # OpenAI official
```

### Giải pháp 3: Dùng LangChain Tools

CrewAI hỗ trợ LangChain tools. Có thể convert:
```python
from langchain.tools import Tool

def search_products(query: str) -> str:
    tool = SupabaseProductSearchTool()
    return tool._run(query)

langchain_tool = Tool(
    name="search_products_supabase",
    description="...",
    func=search_products
)
```

### Giải pháp 4: Simplify Task Description

Rút gọn task description xuống còn 20-30 dòng:
```yaml
description: >
  Customer: {topic}
  
  RULES:
  1. Product questions → call search_products_supabase
  2. Handoff → call handoff_support_via_email
  3. General questions → answer directly
```

### Giải pháp 5: Enable Planning

```python
Crew(
    ...,
    planning=True,  # Enable planning feature
)
```

### Giải pháp 6: Check CrewAI Version

```bash
uv pip list | grep crewai
```

Có thể cần upgrade/downgrade version.

## Next Steps

1. ✅ Test LLM function calling → PASSED
2. ⏳ Simplify task description
3. ⏳ Try different model
4. ⏳ Enable planning
5. ⏳ Check CrewAI version
6. ⏳ Try LangChain tools format

## Tạm kết

Vấn đề KHÔNG PHẢI Ở:
- ❌ Tool implementation
- ❌ LLM model capability
- ❌ Tool descriptions

Vấn đề CÓ THỂ Ở:
- ✅ CrewAI framework không truyền tools đúng cách
- ✅ Task description quá phức tạp
- ✅ Agent config thiếu
- ✅ Model compatibility với CrewAI

## Recommendation

**URGENT: Cần test với model OpenAI official (gpt-4) để xác định vấn đề là ở model hay framework.**

```python
llm = LLM(
    model="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY"),
    # Không dùng base_url
)
```

Nếu gpt-4 hoạt động → Vấn đề ở model cx/gpt-5.2 qua 9router
Nếu gpt-4 KHÔNG hoạt động → Vấn đề ở CrewAI framework hoặc config
