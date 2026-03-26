import json
import os
import urllib.parse
from playwright.sync_api import sync_playwright

def get_tiktok_videos(profile_url, max_videos=10):
    """
    Lấy danh sách video từ TikTok profile
    
    Args:
        profile_url: URL của TikTok profile (vd: https://www.tiktok.com/@username)
        max_videos: Số lượng video tối đa cần lấy (mặc định 10)
    
    Returns:
        List các video với thông tin: id, title, thumbnail, url
    """
    username = profile_url.rstrip('/').split('@')[-1].split('?')[0]
    captured_videos = []
    
    def handle_response(response):
        nonlocal captured_videos
        if "item_list" in response.url:
            try:
                body = response.json()
                items = body.get("itemList", [])
                if items:
                    print(f"✅ Bắt được {len(items)} video từ API: {response.url.split('?')[0]}")
                    for item in items:
                        video_id = item.get("id")
                        title = item.get("desc", "")
                        
                        video_info = item.get("video", {})
                        thumbnail = video_info.get("originCover") or video_info.get("cover") or video_info.get("dynamicCover") or ""
                        
                        if not any(v.get("id") == video_id for v in captured_videos):
                            captured_videos.append({
                                "id": video_id,
                                "title": title.strip(),
                                "thumbnail": thumbnail,
                                "url": f"https://www.tiktok.com/@{username}/video/{video_id}"
                            })
            except Exception as e:
                pass
    
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )

        page = context.new_page()
        page.on("response", handle_response)

        print(f"Mở trang TikTok: {profile_url}")
        page.goto(profile_url, wait_until="domcontentloaded", timeout=60000)
        
        print("Đang cuộn trang để lấy dữ liệu video...")
        for i in range(10):
            page.mouse.wheel(0, 1500)
            page.wait_for_timeout(1000)
            if len(captured_videos) >= max_videos:
                break

        if len(captured_videos) < max_videos:
            print("Chờ thêm mạng lưới...")
            page.wait_for_timeout(5000)

        result_videos = captured_videos[:max_videos]

        if result_videos:
            out_file = f"tiktok_videos_{username}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(result_videos, f, indent=4, ensure_ascii=False)
            print(f"\n🎉 Đã lưu {len(result_videos)} video vào file {out_file}")
            
            print(f"\n--- DANH SÁCH {len(result_videos)} VIDEO GẦN NHẤT ---")
            for idx, vid in enumerate(result_videos, 1):
                print(f"{idx}. {vid['title']}")
                print(f"   Link: {vid['url']}")
        else:
            print("\n❌ KHÔNG thể bắt được API item_list.")

        browser.close()
        return result_videos

if __name__ == "__main__":
    # Test khi chạy trực tiếp
    TARGET_URL = 'https://www.tiktok.com/@cohocchamda'
    videos = get_tiktok_videos(TARGET_URL)
    print(f"\nĐã lấy được {len(videos)} videos")
