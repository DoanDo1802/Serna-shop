"""
Lấy dữ liệu Follower Chart của KOL (Gender, Age, Location, Language, Active Hours)
từ trang chi tiết của Kalodata. Dùng Playwright để intercept API.
"""
import json
import os
import urllib.parse
from playwright.sync_api import sync_playwright

def get_follower_stats(target_url):
    """
    Hàm tự động trích xuất thông tin người theo dõi từ URL của Kalodata KOL.
    Truyền vào 1 Link, trả về Dictionary chứa { majority_gender, top_2_ages, engagement_rate }
    """
    parsed_url = urllib.parse.urlparse(target_url)
    qs = urllib.parse.parse_qs(parsed_url.query)
    creator_id = qs.get('id', ['unknown'])[0]
    
    # Đọc Cookie từ file hoặc môi trường
    import os
    _cookie_file = os.path.join(os.path.dirname(__file__) or ".", ".cookie")
    if os.path.isfile(_cookie_file):
        with open(_cookie_file, "r", encoding="utf-8") as f:
            COOKIE_STR = f.read().split("\n")[0].strip()
    elif os.environ.get("KALODATA_COOKIE"):
        COOKIE_STR = os.environ.get("KALODATA_COOKIE", "")
    else:
        COOKIE_STR = ""
        
    def parse_cookies(s, domain=".kalodata.com", path="/"):
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
        
    # Reset biến toàn cục chứa data trước khi bắt đầu cuộn trang mới
    global captured_data
    captured_data = None
    
    def handle_response(response):
        global captured_data
        if "followerInfoChart" in response.url:
            try:
                body = response.json()
                if body.get("success") and body.get("data"):
                    captured_data = body["data"]
            except Exception as e:
                pass
                
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        if COOKIE_STR:
            context.add_cookies(parse_cookies(COOKIE_STR))
    
        page = context.new_page()
        page.on("response", handle_response)
    
        print(f"🌍 Mở trang biểu đồ KOL: {target_url}")
        page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        
        print("Đang cuộn trang xuống tận đáy để bắt Data...")
        for i in range(15):
            page.mouse.wheel(0, 1500)
            page.wait_for_timeout(800)
            if captured_data:
                break
    
        if not captured_data:
            page.wait_for_timeout(5000)
            
        browser.close()
    
    if captured_data:
        g_male = captured_data.get("followerGenderMale", 0)
        g_female = captured_data.get("followerGenderFemale", 0)
        if g_male > g_female:
            majority_gender = f"Nam ({g_male * 100:.1f}%)"
        else:
            majority_gender = f"Nữ ({g_female * 100:.1f}%)"
        
        ages = captured_data.get("ages", [])
        sorted_ages = sorted(ages, key=lambda x: float(x.get("value", 0)), reverse=True)
        top_2_ages = [f"{age_group.get('name', '')} ({float(age_group.get('value', 0)) * 100:.1f}%)" for age_group in sorted_ages[:2]]
        
        engagement_rate_raw = captured_data.get("engagementRate", "0%")
        # Đảm bảo format ra đúng tỷ lệ
        
        trimmed_data = {
            "creator_id": creator_id,
            "majority_gender": majority_gender,
            "top_2_ages": ", ".join(top_2_ages) if top_2_ages else "", # Gom ["18-24", "25-34"] thành chuỗi "18-24, 25-34"
            "engagement_rate": engagement_rate_raw
        }
        print(f"✅ Lấy Data THÀNH CÔNG: {trimmed_data}")
        return trimmed_data
    else:
        print(f"❌ THẤT BẠI khi lấy link KOL: {target_url}")
        return None

if __name__ == "__main__":
    TARGET_URL = 'https://www.kalodata.com/creator/detail?id=7371393642286711816&language=vi-VN&currency=VND&region=VN&dateRange=%5B%222026-02-07%22%2C%222026-03-08%22%5D'
    data = get_follower_stats(TARGET_URL)
    if data:
        out_file = f"follower_info_{data['creator_id']}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
