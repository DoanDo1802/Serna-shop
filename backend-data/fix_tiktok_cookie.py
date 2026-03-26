#!/usr/bin/env python3
"""
Script để convert TikTok cookie từ text sang JSON format
"""
import os
import json
from datetime import datetime

def parse_cookies_to_json(cookie_str, domain=".tiktok.com"):
    """Convert cookie string to JSON format"""
    cookies = []
    for part in cookie_str.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        name, _, value = part.partition("=")
        name, value = name.strip(), value.strip()
        if name:
            cookies.append({
                "name": name,
                "value": value,
                "domain": domain,
                "path": "/",
                "expires": -1  # No expiry info from text format
            })
    return cookies

def main():
    print("🔧 TikTok Cookie Fixer")
    print("="*60)
    
    # Read text cookie
    cookie_file = os.path.join(os.path.dirname(__file__), "tiktok", ".tiktok_cookie")
    json_file = os.path.join(os.path.dirname(__file__), "tiktok", ".tiktok_cookie.json")
    
    if not os.path.exists(cookie_file):
        print(f"❌ File không tồn tại: {cookie_file}")
        return
    
    with open(cookie_file, 'r', encoding='utf-8') as f:
        cookie_str = f.read().strip()
    
    print(f"✅ Đọc cookie từ: {cookie_file}")
    print(f"   Length: {len(cookie_str)} chars")
    
    # Parse to JSON
    cookies = parse_cookies_to_json(cookie_str)
    print(f"✅ Parsed {len(cookies)} cookies")
    
    # Save JSON
    data = {
        "cookies": cookies,
        "updated_at": datetime.now().isoformat()
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Đã lưu JSON: {json_file}")
    
    # Validate
    important_cookies = ["sessionid", "sid_tt", "uid_tt", "cmpl_token"]
    cookie_names = [c["name"] for c in cookies]
    found = [name for name in important_cookies if name in cookie_names]
    
    if found:
        print(f"\n✅ Cookie hợp lệ! Tìm thấy: {', '.join(found)}")
    elif len(cookies) >= 5:
        print(f"\n✅ Cookie hợp lệ! Có {len(cookies)} cookies (guest mode)")
    else:
        print(f"\n⚠️  Cookie có thể không đủ. Chỉ có {len(cookies)} cookies")
        print(f"   Thử refresh: python3 update_cookies.py --tiktok --force")
    
    print(f"\n💡 Giờ bạn có thể:")
    print(f"   1. Reload Settings page")
    print(f"   2. Hoặc restart backend")

if __name__ == "__main__":
    main()
