"""Simple tools using @tool decorator for testing."""

from crewai.tools import tool
from agent_sale.tools.supabase_product_search_tool import SupabaseProductSearchTool
from agent_sale.tools.email_handoff_tool import EmailHandoffTool


@tool("search_products_supabase")
def search_products_supabase(search_query: str) -> str:
    """
    **CRITICAL: Use this tool WHENEVER customer asks about products, prices, or models.**
    
    Searches IonQ hair dryer products in Supabase database.
    
    **MUST USE when customer asks:**
    - 'Có sản phẩm gì?', 'Có sản phẩm j?', 'Có máy nào?'
    - 'Giá bao nhiêu?', 'Máy giá rẻ', 'Tầm 500k'
    - 'Tư vấn máy', 'Gợi ý máy', 'Máy nào tốt?'
    
    Use search_query='*' to see all products.
    
    Args:
        search_query: Search term or '*' for all products
    
    Returns:
        List of products with names, prices, and descriptions
    """
    tool_instance = SupabaseProductSearchTool()
    return tool_instance._run(search_query=search_query)


@tool("handoff_support_via_email")
def handoff_support_via_email(
    customer_name: str,
    customer_phone: str,
    issue: str,
    product_model: str = "",
    chat_history_json: str = ""
) -> str:
    """
    **CRITICAL: Use this tool to send handoff email to support team.**
    
    Sends email when agent cannot handle the issue.
    
    **MUST USE when:**
    - Customer requests warranty, returns, or exchanges
    - Customer wants to contact management
    - Product is broken and needs repair
    
    **IMPORTANT: Only call AFTER getting customer name and phone!**
    
    Args:
        customer_name: Customer's full name
        customer_phone: Customer's phone number
        issue: Description of the issue
        product_model: (Optional) Product model
        chat_history_json: (Optional) Chat history as JSON
    
    Returns:
        Confirmation message
    """
    tool_instance = EmailHandoffTool()
    return tool_instance._run(
        customer_name=customer_name,
        customer_phone=customer_phone,
        issue=issue,
        product_model=product_model if product_model else None,
        chat_history_json=chat_history_json if chat_history_json else None
    )
