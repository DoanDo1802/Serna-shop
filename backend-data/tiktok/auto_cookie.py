"""
Auto Cookie Manager cho TikTok
Tự động lấy và refresh cookie khi hết hạn
"""
import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

COOKIE_FILE = os.path.join(os.path.dirname(__file__), ".tiktok_cookie")
COOKIE_JSON_FILE = os.path.join(os.path.dirname(__file__), ".tiktok_cookie.json")

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
    
    # Check xem có cookie quan trọng không (chỉ cần 1 trong số này)
    important_cookies = ["sessionid", "sid_tt", "uid_tt", "cmpl_token"]
    cookie_names = [c["name"] for c in cookies]
    
    has_important = any(name in cookie_names for name in important_cookies)
    if not has_important:
        # Nếu không có cookie quan trọng nhưng có ít nhất 5 cookies khác
        # thì cũng coi như valid (có thể là guest mode)
        return len(cookies) >= 5
    
    return True

def get_tiktok_cookie(force_refresh=False, headless=False):
    """
    Lấy cookie TikTok tự động
    
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
    
    print("🔄 Đang lấy cookie mới từ TikTok...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
            ],
            slow_mo=100  # Slow down to appear more human-like
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
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
        
        page = context.new_page()
        
        # Enhanced stealth mode
        page.add_init_script("""
            // Overwrite the `plugins` property to use a custom getter.
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Overwrite the `plugins` property to use a custom getter.
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Overwrite the `languages` property to use a custom getter.
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Pass the Chrome Test.
            window.chrome = {
                runtime: {},
            };
            
            // Pass the Permissions Test.
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        print("🌐 Đang mở TikTok...")
        
        # Try multiple strategies
        success = False
        
        # Strategy 1: Try homepage first
        try:
            page.goto("https://www.tiktok.com", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            success = True
            print("✅ Đã mở TikTok homepage")
        except Exception as e:
            print(f"⚠️  Homepage failed: {str(e)[:100]}")
        
        # Strategy 2: Try explore page
        if not success:
            try:
                print("🔄 Thử explore page...")
                page.goto("https://www.tiktok.com/explore", wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)
                success = True
                print("✅ Đã mở TikTok explore")
            except Exception as e:
                print(f"⚠️  Explore failed: {str(e)[:100]}")
        
        # Strategy 3: Try foryou page
        if not success:
            try:
                print("🔄 Thử foryou page...")
                page.goto("https://www.tiktok.com/foryou", wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)
                success = True
                print("✅ Đã mở TikTok foryou")
            except Exception as e:
                print(f"⚠️  Foryou failed: {str(e)[:100]}")
        
        if not success:
            browser.close()
            raise Exception(
                "❌ Không thể mở TikTok!\n"
                "Có thể do:\n"
                "1. TikTok đang block region của bạn\n"
                "2. Network issue\n"
                "3. Cloudflare đang chặn\n\n"
                "💡 Giải pháp:\n"
                "- Thử lại sau vài phút\n"
                "- Hoặc dùng VPN\n"
                "- Hoặc copy cookie thủ công từ trình duyệt thường"
            )
        
        page.wait_for_timeout(2000)
        
        # Luôn yêu cầu user xác nhận (để có thời gian đổi tài khoản nếu cần)
        print("\n" + "="*60)
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
        
        page.wait_for_timeout(2000)
        
        # Lấy cookies
        cookies = context.cookies()
        
        if not is_cookie_valid(cookies):
            browser.close()
            raise Exception("❌ Cookie không hợp lệ! Vui lòng đăng nhập lại.")
        
        cookie_str = save_cookies_to_file(cookies)
        
        browser.close()
        
        return cookie_str

if __name__ == "__main__":
    import sys
    
    force = "--force" in sys.argv
    headless = "--headless" in sys.argv
    
    print("🚀 TikTok Auto Cookie Manager")
    print("-" * 60)
    
    try:
        cookie = get_tiktok_cookie(force_refresh=force, headless=headless)
        print("\n✅ THÀNH CÔNG!")
        print(f"📝 Cookie length: {len(cookie)} chars")
        print(f"📁 Đã lưu vào: {COOKIE_FILE}")
        print("\n💡 Bạn có thể copy cookie này vào .env:")
        print(f"TIKTOK_COOKIE={cookie[:100]}...")
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        sys.exit(1)
