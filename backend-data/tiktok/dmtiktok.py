"""
Gửi tin nhắn (DM) tự động trên TikTok bằng Playwright.
Sử dụng Cookie do User cung cấp để giữ trạng thái đăng nhập.
"""
import os
import time
from playwright.sync_api import sync_playwright
import requests

def get_default_cookie():
    """Đọc Cookie từ file hoặc biến môi trường - ĐỘNG, không cache"""
    _cookie_file = os.path.join(os.path.dirname(__file__) or ".", ".tiktok_cookie")
    
    # Ưu tiên đọc từ file (mới nhất)
    if os.path.isfile(_cookie_file):
        with open(_cookie_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    
    # Fallback sang env
    if os.environ.get("TIKTOK_COOKIE"):
        return os.environ.get("TIKTOK_COOKIE", "")
    
    return ""

def parse_cookies(s, domain=".tiktok.com", path="/"):
    """Chuyển chuỗi cookie thành list dict cho Playwright"""
    out = []
    for part in s.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        name, _, value = part.partition("=")
        name, value = name.strip(), value.strip()
        if name:
            out.append({"name": name, "value": value, "domain": domain, "path": path})
    return out

def get_uid_from_username(username):
    """Lấy UID từ username TikTok"""
    print(f"Bắt đầu lấy UID cho username: {username}...")
    api_url = f"https://www.tikwm.com/api/user/info?unique_id={username}"
    try:
        res = requests.get(api_url)
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == 0 and "data" in data and "user" in data["data"]:
                uid = data["data"]["user"]["id"]
                print(f"✅ Đã phân giải thành công UID: {uid}")
                return uid
    except Exception as e:
        print(f"Lỗi khi lấy UID: {e}")
    return None

def send_tiktok_dm_to_user(profile_url, message, cookie_string=None):
    """
    Gửi tin nhắn TikTok tự động
    
    Args:
        profile_url: URL profile TikTok (vd: https://www.tiktok.com/@username)
        message: Nội dung tin nhắn
        cookie_string: Cookie đăng nhập (optional, sẽ đọc từ file nếu không có)
    
    Returns:
        Dict với status và message
    """
    if cookie_string is None:
        cookie_string = get_default_cookie()
    
    if not cookie_string:
        return {"success": False, "error": "Thiếu cookie đăng nhập TikTok"}
    
    username_raw = profile_url.rstrip('/').split('@')[-1].split('?')[0]
    
    uid = get_uid_from_username(username_raw)
    if not uid:
        return {"success": False, "error": "Không thể lấy UID từ username"}

    direct_msg_url = f"https://www.tiktok.com/messages?lang=vi-VN&u={uid}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        print("Đang nạp Cookie đăng nhập...")
        context.add_cookies(parse_cookies(cookie_string))
        
        page = context.new_page()
        
        try:
            print(f"🌍 Truy cập URL tin nhắn: {direct_msg_url}")
            page.goto(direct_msg_url, wait_until="domcontentloaded", timeout=60000)
            print("⏳ Đang đợi trang chat tải...")
            page.wait_for_timeout(15000)
            
            print("⌨️  Đang tìm ô nhập tin nhắn...")
            
            chat_box = None
            locators_to_try = [
                "div[data-contents='true']",
                ".public-DraftEditor-content",
                "[data-e2e='message-input']",
                "input[placeholder*='tin nhắn']",
                "input[placeholder*='message']",
                "div[role='textbox']"
            ]
            
            for selector in locators_to_try:
                elem = page.locator(selector).first
                if elem.is_visible():
                    chat_box = elem
                    print(f"✅ Đã tìm thấy ô nhập liệu: {selector}")
                    break
                
            if chat_box:
                chat_box.click()
                page.keyboard.type(message, delay=100)
                page.wait_for_timeout(1000)
                
                print("🚀 Đang bấm Gửi (Enter)...")
                page.keyboard.press("Enter")
                
                print("✅ TIN NHẮN ĐÃ ĐƯỢC GỬI THÀNH CÔNG!")
                page.wait_for_timeout(3000)
                
                browser.close()
                return {"success": True, "message": "Đã gửi tin nhắn thành công"}
            else:
                print("❌ Không tìm thấy ô nhập tin nhắn")
                page.screenshot(path="tiktok_error_chatbox.png")
                browser.close()
                return {"success": False, "error": "Không tìm thấy ô nhập tin nhắn"}
                
        except Exception as e:
            print(f"❌ Có lỗi: {e}")
            browser.close()
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Test khi chạy trực tiếp
    TARGET_USER_URL = "https://www.tiktok.com/@doando1802"
    MESSAGE_TEXT = "chúng ta có thể hợp tác ko"
    result = send_tiktok_dm_to_user(TARGET_USER_URL, MESSAGE_TEXT)
    print(result)
