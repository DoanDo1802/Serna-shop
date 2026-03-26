"""
Agent gợi ý filter Kalodata dựa trên sản phẩm.
Sử dụng LLM qua OpenAI-compatible API (9router).
"""

import json
import base64
import os
import requests
from .skills import SYSTEM_PROMPT

# LLM Config - đọc từ .env
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:20128/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "cx/gpt-5.2")


def suggest_filters(description: str, price: str = "", image_base64: str = None, image_url: str = None) -> dict:
    """
    Gọi LLM để gợi ý filter Kalodata phù hợp với sản phẩm.

    Args:
        description: Mô tả sản phẩm
        price: Giá bán (VND)
        image_base64: Ảnh sản phẩm dạng base64 (optional)
        image_url: URL ảnh sản phẩm (optional)

    Returns:
        dict với keys: explanation, filters
    """
    # Build text prompt (model doesn't support vision, so skip image)
    text_prompt = f"Sản phẩm: {description}"
    if price:
        text_prompt += f"\nGiá bán: {price} VND"
    text_prompt += "\n\nHãy gợi ý các filter Kalodata phù hợp nhất để tìm KOL bán sản phẩm này."

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text_prompt},
    ]

    try:
        response = requests.post(
            f"{LLM_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": LLM_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]
        print(f"🤖 Agent raw response:\n{content}")

        # Parse JSON from response (handle markdown code blocks)
        json_str = content.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()

        result = json.loads(json_str)

        # Validate structure
        if "explanation" not in result or "filters" not in result:
            return {
                "explanation": content,
                "filters": {},
                "raw": content,
            }

        return result

    except requests.exceptions.ConnectionError:
        raise Exception("Không thể kết nối đến LLM server. Hãy kiểm tra server đang chạy tại " + LLM_BASE_URL)
    except requests.exceptions.Timeout:
        raise Exception("LLM server không phản hồi trong 60 giây.")
    except json.JSONDecodeError:
        # Return raw text if can't parse JSON
        return {
            "explanation": content if 'content' in dir() else "Không thể parse response từ LLM",
            "filters": {},
            "raw": content if 'content' in dir() else "",
        }
    except Exception as e:
        raise Exception(f"Lỗi khi gọi LLM: {str(e)}")

