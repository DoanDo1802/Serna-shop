#!/usr/bin/env python3
"""
Script để test và debug cookie status
"""
import os
import json
import sys
from datetime import datetime

def check_cookie_file(cookie_file, platform_name):
    """Kiểm tra cookie file"""
    print(f"\n{'='*60}")
    print(f"🔍 Kiểm tra {platform_name} Cookie")
    print(f"{'='*60}")
    
    # Check text file
    text_file = cookie_file.replace('.json', '')
    if os.path.exists(text_file):
        with open(text_file, 'r') as f:
            cookie_str = f.read().strip()
            print(f"✅ File text: {text_file}")
            print(f"   Length: {len(cookie_str)} chars")
            print(f"   Preview: {cookie_str[:100]}...")
    else:
        print(f"❌ File text không tồn tại: {text_file}")
    
    # Check JSON file
    if os.path.exists(cookie_file):
        try:
            with open(cookie_file, 'r') as f:
                data = json.load(f)
                cookies = data.get('cookies', [])
                updated_at = data.get('updated_at', 'Unknown')
                
                print(f"\n✅ File JSON: {cookie_file}")
                print(f"   Số lượng cookies: {len(cookies)}")
                print(f"   Cập nhật lúc: {updated_at}")
                
                # List cookie names
                if cookies:
                    print(f"\n   📋 Danh sách cookies:")
                    for i, cookie in enumerate(cookies[:10], 1):
                        name = cookie.get('name', 'unknown')
                        value_len = len(cookie.get('value', ''))
                        domain = cookie.get('domain', 'unknown')
                        print(f"      {i}. {name} ({value_len} chars) - {domain}")
                    
                    if len(cookies) > 10:
                        print(f"      ... và {len(cookies) - 10} cookies khác")
                
                return cookies
        except Exception as e:
            print(f"❌ Lỗi đọc JSON: {e}")
            return []
    else:
        print(f"❌ File JSON không tồn tại: {cookie_file}")
        return []

def check_env_cookie(key):
    """Kiểm tra cookie trong .env"""
    cookie = os.environ.get(key)
    if cookie:
        print(f"\n✅ Environment variable: {key}")
        print(f"   Length: {len(cookie)} chars")
        print(f"   Preview: {cookie[:100]}...")
        return True
    else:
        print(f"\n❌ Environment variable không có: {key}")
        return False

def validate_tiktok_cookie(cookies):
    """Validate TikTok cookie"""
    if not cookies:
        return False, "Không có cookies"
    
    important_cookies = ["sessionid", "sid_tt", "uid_tt", "cmpl_token"]
    cookie_names = [c["name"] for c in cookies]
    
    found = [name for name in important_cookies if name in cookie_names]
    
    if found:
        return True, f"Tìm thấy cookies quan trọng: {', '.join(found)}"
    elif len(cookies) >= 5:
        return True, f"Có {len(cookies)} cookies (guest mode)"
    else:
        return False, f"Chỉ có {len(cookies)} cookies, không đủ"

def validate_kalodata_cookie(cookies):
    """Validate Kalodata cookie"""
    if not cookies:
        return False, "Không có cookies"
    
    important_cookies = ["SESSION", "sid_guard", "deviceId"]
    cookie_names = [c["name"] for c in cookies]
    
    found = [name for name in important_cookies if name in cookie_names]
    
    if found:
        return True, f"Tìm thấy cookies quan trọng: {', '.join(found)}"
    elif len(cookies) >= 10:
        return True, f"Có {len(cookies)} cookies"
    else:
        return False, f"Chỉ có {len(cookies)} cookies, không đủ"

def main():
    print("🚀 Cookie Status Checker")
    print("="*60)
    
    # Load .env
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check Kalodata
    kalodata_json = os.path.join(os.path.dirname(__file__), "kalodata", ".cookie.json")
    kalodata_cookies = check_cookie_file(kalodata_json, "Kalodata")
    check_env_cookie("KALODATA_COOKIE")
    
    valid, msg = validate_kalodata_cookie(kalodata_cookies)
    print(f"\n{'✅' if valid else '❌'} Validation: {msg}")
    
    # Check TikTok
    tiktok_json = os.path.join(os.path.dirname(__file__), "tiktok", ".tiktok_cookie.json")
    tiktok_cookies = check_cookie_file(tiktok_json, "TikTok")
    check_env_cookie("TIKTOK_COOKIE")
    
    valid, msg = validate_tiktok_cookie(tiktok_cookies)
    print(f"\n{'✅' if valid else '❌'} Validation: {msg}")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Tóm tắt")
    print(f"{'='*60}")
    
    kalodata_valid, _ = validate_kalodata_cookie(kalodata_cookies)
    tiktok_valid, _ = validate_tiktok_cookie(tiktok_cookies)
    
    print(f"Kalodata: {'✅ Hợp lệ' if kalodata_valid else '❌ Không hợp lệ'}")
    print(f"TikTok:   {'✅ Hợp lệ' if tiktok_valid else '❌ Không hợp lệ'}")
    
    if not kalodata_valid or not tiktok_valid:
        print(f"\n💡 Để refresh cookie:")
        print(f"   python3 update_cookies.py --force")
        print(f"   Hoặc dùng Settings page trên frontend")

if __name__ == "__main__":
    main()
