#!/usr/bin/env python3
"""
Script tự động update cookies vào file .env
Chạy: python3 update_cookies.py [--kalodata] [--tiktok] [--force]
"""
import os
import sys
import re

# Add paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from kalodata.auto_cookie import get_kalodata_cookie
from tiktok.auto_cookie import get_tiktok_cookie

ENV_FILE = os.path.join(ROOT_DIR, ".env")

def update_env_file(key, value):
    """Update hoặc thêm key=value vào file .env"""
    if not os.path.exists(ENV_FILE):
        print(f"⚠️ File .env không tồn tại, tạo mới...")
        with open(ENV_FILE, "w") as f:
            f.write(f"{key}={value}\n")
        return
    
    # Đọc file .env
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Tìm và update key
    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            updated = True
            break
    
    # Nếu không tìm thấy, thêm vào cuối
    if not updated:
        lines.append(f"\n{key}={value}\n")
    
    # Ghi lại file
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    print(f"✅ Đã update {key} trong {ENV_FILE}")

def main():
    args = sys.argv[1:]
    
    update_kalodata = "--kalodata" in args
    update_tiktok = "--tiktok" in args
    force = "--force" in args
    
    # Nếu không chỉ định cái nào, thì update cả 2
    if not update_kalodata and not update_tiktok:
        update_kalodata = True
        update_tiktok = True
    
    print("🚀 Auto Cookie Updater")
    print("=" * 60)
    
    success_count = 0
    
    # Update Kalodata cookie
    if update_kalodata:
        print("\n📊 KALODATA")
        print("-" * 60)
        try:
            cookie = get_kalodata_cookie(force_refresh=force, headless=False)
            update_env_file("KALODATA_COOKIE", cookie)
            success_count += 1
        except Exception as e:
            print(f"❌ Lỗi Kalodata: {e}")
    
    # Update TikTok cookie
    if update_tiktok:
        print("\n🎵 TIKTOK")
        print("-" * 60)
        try:
            cookie = get_tiktok_cookie(force_refresh=force, headless=False)
            update_env_file("TIKTOK_COOKIE", cookie)
            success_count += 1
        except Exception as e:
            print(f"❌ Lỗi TikTok: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if success_count > 0:
        print(f"✅ Đã update {success_count} cookie(s) thành công!")
        print(f"📁 File: {ENV_FILE}")
        print("\n💡 Giờ bạn có thể chạy app mà không cần copy cookie thủ công")
    else:
        print("❌ Không update được cookie nào")
        sys.exit(1)

if __name__ == "__main__":
    main()
