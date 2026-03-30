#!/usr/bin/env python3
"""
Script để switch giữa nhiều tài khoản
"""
import os
import sys
import shutil
import json

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "cookie_profiles")

def list_profiles(platform):
    """List all saved profiles"""
    platform_dir = os.path.join(PROFILES_DIR, platform)
    if not os.path.exists(platform_dir):
        return []
    
    profiles = []
    for item in os.listdir(platform_dir):
        if item.endswith('.json'):
            profile_name = item.replace('.json', '')
            profiles.append(profile_name)
    
    return profiles

def save_profile(platform, profile_name):
    """Save current cookie as a profile"""
    platform_dir = os.path.join(PROFILES_DIR, platform)
    os.makedirs(platform_dir, exist_ok=True)
    
    # Source files
    if platform == "kalodata":
        src_json = os.path.join(os.path.dirname(__file__), "kalodata", ".cookie.json")
        src_txt = os.path.join(os.path.dirname(__file__), "kalodata", ".cookie")
    else:  # tiktok
        src_json = os.path.join(os.path.dirname(__file__), "tiktok", ".tiktok_cookie.json")
        src_txt = os.path.join(os.path.dirname(__file__), "tiktok", ".tiktok_cookie")
    
    # Destination files
    dst_json = os.path.join(platform_dir, f"{profile_name}.json")
    dst_txt = os.path.join(platform_dir, f"{profile_name}.txt")
    
    # Copy files
    if os.path.exists(src_json):
        shutil.copy2(src_json, dst_json)
        print(f"✅ Đã lưu JSON: {dst_json}")
    
    if os.path.exists(src_txt):
        shutil.copy2(src_txt, dst_txt)
        print(f"✅ Đã lưu TXT: {dst_txt}")
    
    # Save metadata
    with open(dst_json, 'r') as f:
        data = json.load(f)
    
    cookies = data.get('cookies', [])
    print(f"✅ Profile '{profile_name}' đã được lưu với {len(cookies)} cookies")

def load_profile(platform, profile_name):
    """Load a saved profile"""
    platform_dir = os.path.join(PROFILES_DIR, platform)
    
    # Source files
    src_json = os.path.join(platform_dir, f"{profile_name}.json")
    src_txt = os.path.join(platform_dir, f"{profile_name}.txt")
    
    if not os.path.exists(src_json):
        print(f"❌ Profile '{profile_name}' không tồn tại!")
        return False
    
    # Destination files
    if platform == "kalodata":
        dst_json = os.path.join(os.path.dirname(__file__), "kalodata", ".cookie.json")
        dst_txt = os.path.join(os.path.dirname(__file__), "kalodata", ".cookie")
    else:  # tiktok
        dst_json = os.path.join(os.path.dirname(__file__), "tiktok", ".tiktok_cookie.json")
        dst_txt = os.path.join(os.path.dirname(__file__), "tiktok", ".tiktok_cookie")
    
    # Copy files
    shutil.copy2(src_json, dst_json)
    print(f"✅ Đã load JSON: {dst_json}")
    
    if os.path.exists(src_txt):
        shutil.copy2(src_txt, dst_txt)
        print(f"✅ Đã load TXT: {dst_txt}")
    
    # Update .env
    with open(dst_txt, 'r') as f:
        cookie_str = f.read().strip()
    
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    key = "KALODATA_COOKIE" if platform == "kalodata" else "TIKTOK_COOKIE"
    
    # Read .env
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update key
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={cookie_str}\n"
                updated = True
                break
        
        if not updated:
            lines.append(f"\n{key}={cookie_str}\n")
        
        # Write back
        with open(env_file, 'w') as f:
            f.writelines(lines)
    
    print(f"✅ Đã update .env")
    print(f"\n💡 Giờ bạn cần restart backend để áp dụng thay đổi")
    
    return True

def main():
    if len(sys.argv) < 2:
        print("🔄 Account Switcher")
        print("="*60)
        print("\nUsage:")
        print("  python3 switch_account.py list <platform>")
        print("  python3 switch_account.py save <platform> <profile_name>")
        print("  python3 switch_account.py load <platform> <profile_name>")
        print("\nPlatform: kalodata | tiktok")
        print("\nExamples:")
        print("  python3 switch_account.py list tiktok")
        print("  python3 switch_account.py save tiktok user1")
        print("  python3 switch_account.py load tiktok user1")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        if len(sys.argv) < 3:
            print("❌ Missing platform. Usage: list <platform>")
            return
        
        platform = sys.argv[2]
        profiles = list_profiles(platform)
        
        print(f"\n📋 Profiles cho {platform}:")
        print("="*60)
        if profiles:
            for i, profile in enumerate(profiles, 1):
                print(f"  {i}. {profile}")
        else:
            print("  (Chưa có profile nào)")
        print()
    
    elif command == "save":
        if len(sys.argv) < 4:
            print("❌ Missing arguments. Usage: save <platform> <profile_name>")
            return
        
        platform = sys.argv[2]
        profile_name = sys.argv[3]
        
        print(f"\n💾 Đang lưu profile '{profile_name}' cho {platform}...")
        print("="*60)
        save_profile(platform, profile_name)
    
    elif command == "load":
        if len(sys.argv) < 4:
            print("❌ Missing arguments. Usage: load <platform> <profile_name>")
            return
        
        platform = sys.argv[2]
        profile_name = sys.argv[3]
        
        print(f"\n📂 Đang load profile '{profile_name}' cho {platform}...")
        print("="*60)
        load_profile(platform, profile_name)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Valid commands: list, save, load")

if __name__ == "__main__":
    main()
