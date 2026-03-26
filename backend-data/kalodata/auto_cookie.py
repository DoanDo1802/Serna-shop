"""
Auto Cookie Manager cho Kalodata
Tự động lấy và refresh cookie khi hết hạn
"""
import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

COOKIE_FILE = os.path.join(os.path.dirname(__file__), ".cookie")
COOKIE_JSON_FILE = os.path.join(os.path.dirname(__file__), ".cookie.json")

def save_cookies_to_file(cookies, cookie_file=COOKIE_FILE):
    """Lưu cookies vào file text và JSON"""
    # Lưu dạng string (cho .env)
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(cookie_str)
    
    # Lưu dạng JSON (để check expiry)
    with open(COOKIE_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "cookies": cookies,
            "updated_at": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"✅ Đã lưu cookie vào {cookie_file}")
    return cookie_str

def load_cookies_from_file():
    """Load cookies từ file JSON"""
    if not os.path.exists(COOKIE_JSON_FILE):
        return None
    
    try:
        with open(COOKIE_JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("cookies", [])
    except:
        return None

def is_cookie_valid(cookies):
    """Kiểm tra cookie còn hạn không"""
    if not cookies:
        return False
    
    # Check xem có cookie quan trọng không
    important_cookies = ["SESSION", "sid_guard"]
    cookie_names = [c["name"] for c in cookies]
    
    for name in important_cookies:
        if name not in cookie_names:
            return False
    
    # Check expiry
    for cookie in cookies:
        if cookie.get("name") in important_cookies:
            expires = cookie.get("expires", -1)
            if expires > 0 and expires < datetime.now().timestamp():
                print(f"⚠️ Cookie {cookie['name']} đã hết hạn")
                return False
    
    return True

def get_kalodata_cookie(force_refresh=False, headless=False):
    """
    Lấy cookie Kalodata tự động
    
    Args:
        force_refresh: Bắt buộc refresh cookie mới
        headless: Chạy ẩn trình duyệt (False = hiện trình duyệt để đăng nhập)
    
    Returns:
        Cookie string
    """
    # Kiểm tra cookie cũ
    if not force_refresh:
        old_cookies = load_cookies_from_file()
        if is_cookie_valid(old_cookies):
            print("✅ Cookie hiện tại vẫn còn hạn")
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in old_cookies])
            return cookie_str
    
    print("🔄 Đang lấy cookie mới từ Kalodata...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="vi-VN",
            timezone_id="Asia/Ho_Chi_Minh",
        )
        
        # KHÔNG load cookie cũ khi force_refresh = True
        if not force_refresh:
            old_cookies = load_cookies_from_file()
            if old_cookies:
                try:
                    context.add_cookies(old_cookies)
                    print("📦 Đã load cookie cũ")
                except:
                    pass
        else:
            print("🔄 Force refresh - Không load cookie cũ (để bạn có thể đổi tài khoản)")
        if old_cookies:
            try:
                context.add_cookies(old_cookies)
                print("📦 Đã load cookie cũ")
            except:
                pass
        
        page = context.new_page()
        
        # Stealth mode
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        print("🌐 Đang mở Kalodata...")
        page.goto("https://www.kalodata.com/creator", wait_until="domcontentloaded", timeout=60000)
        
        # Đợi Cloudflare
        try:
            page.wait_for_function(
                """() => !document.body.innerText.includes('Just a moment')""",
                timeout=30000
            )
        except:
            pass
        
        page.wait_for_timeout(3000)
        
        # Kiểm tra xem đã login chưa và luôn yêu cầu xác nhận
        current_url = page.url
        
        print("\n" + "="*60)
        if "login" in current_url.lower():
            print("⚠️  BẠN CẦN ĐĂNG NHẬP")
            print("="*60)
            print("1. Trình duyệt đã mở trang login Kalodata")
            print("2. Vui lòng đăng nhập bằng tài khoản của bạn")
        else:
            if force_refresh:
                print("🔄 FORCE REFRESH MODE")
                print("="*60)
                print("Bạn có thể:")
                print("1. Giữ nguyên tài khoản hiện tại (nếu đã login)")
                print("2. Logout và đăng nhập tài khoản khác")
                print("3. Đăng nhập nếu chưa login")
            else:
                print("⚠️  XÁC NHẬN ĐĂNG NHẬP")
                print("="*60)
                print("Vui lòng kiểm tra:")
                print("1. Đã đăng nhập đúng tài khoản chưa?")
                print("2. Nếu chưa login, hãy đăng nhập")
        print("="*60)
        input("\n👉 Nhấn ENTER khi đã sẵn sàng...")
        
        # Đợi một chút
        page.wait_for_timeout(2000)
        
        # Kiểm tra lại URL
        current_url = page.url
        if "login" in current_url.lower():
            browser.close()
            raise Exception("❌ Vẫn chưa đăng nhập thành công!")
        
        print("✅ Đã đăng nhập thành công!")
        
        # Lấy cookies
        cookies = context.cookies()
        cookie_str = save_cookies_to_file(cookies)
        
        browser.close()
        
        return cookie_str

if __name__ == "__main__":
    import sys
    
    force = "--force" in sys.argv
    headless = "--headless" in sys.argv
    
    print("🚀 Kalodata Auto Cookie Manager")
    print("-" * 60)
    
    try:
        cookie = get_kalodata_cookie(force_refresh=force, headless=headless)
        print("\n✅ THÀNH CÔNG!")
        print(f"📝 Cookie length: {len(cookie)} chars")
        print(f"📁 Đã lưu vào: {COOKIE_FILE}")
        print("\n💡 Bạn có thể copy cookie này vào .env:")
        print(f"KALODATA_COOKIE={cookie[:100]}...")
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        sys.exit(1)
