#!/usr/bin/env python3
"""Test if LLM model supports function calling."""

import os
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

# Test function calling capability
def test_function_calling():
    print("="*80)
    print("Testing LLM Function Calling Support")
    print("="*80)
    print()
    
    # Define a simple function
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_products",
                "description": "Search for products in database. Use when customer asks about products.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    messages = [
        {
            "role": "system",
            "content": "You are a sales assistant. When customer asks about products, use the search_products function."
        },
        {
            "role": "user",
            "content": "Có sản phẩm j?"
        }
    ]
    
    try:
        print("Calling LLM with function definition...")
        print(f"Model: {os.getenv('MODEL')}")
        print(f"Base URL: {os.getenv('OPENAI_API_BASE')}")
        print()
        
        response = completion(
            model=os.getenv("MODEL", "openai/cx/gpt-5.2"),
            messages=messages,
            tools=tools,
            tool_choice="auto",
            api_base=os.getenv("OPENAI_API_BASE"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        print("Response:")
        print(response)
        print()
        
        # Check if function was called
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            print("✅ SUCCESS: Model called the function!")
            print(f"Function: {response.choices[0].message.tool_calls[0].function.name}")
            print(f"Arguments: {response.choices[0].message.tool_calls[0].function.arguments}")
        else:
            print("❌ FAIL: Model did NOT call the function")
            print(f"Response content: {response.choices[0].message.content}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_function_calling()
