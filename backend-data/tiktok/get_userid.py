import requests
import sys

def get_tiktok_userid(profile_url):
    """
    Lấy User ID (uid) và SecUid của user TikTok dựa vào username.
    Dùng API của TikWM cho tốc độ cực nhanh và đáng tin cậy.
    """
    # Lấy username từ đường dẫn (loại bỏ dấu @)
    # Ví dụ: https://www.tiktok.com/@123_phoi -> 123_phoi
    username = profile_url.rstrip('/').split('@')[-1].split('?')[0]
    
    print(f"Đang lấy thông tin ID cho username: {username} ...")
    
    api_url = f"https://www.tikwm.com/api/user/info?unique_id={username}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0 and "data" in data and "user" in data["data"]:
                user_info = data["data"]["user"]
                
                print("\n=== THÔNG TIN USER TIKTOK ===")
                print(f"Tên hiển thị: {user_info.get('nickname')}")
                print(f"ID (uid)    : {user_info.get('id')}")
                print(f"SecUid      : {user_info.get('secUid')}")
                
                stats = data["data"].get("stats", {})
                print(f"\n[Thống kê] Follow: {stats.get('followerCount')} | Video: {stats.get('videoCount')}")
            else:
                print(f"❌ Không tìm thấy user hoặc lỗi từ API: {data.get('msg')}")
        else:
            print(f"❌ Lỗi kết nối HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    url = "https://www.tiktok.com/@maianh83838?lang=vi-VN"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    get_tiktok_userid(url)
