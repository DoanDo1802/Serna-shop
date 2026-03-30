"""
Test script để kiểm tra flow cache của KOL ranking
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from kol_management.supabase_kol_store import get_kol_ranking_from_db, save_kol_ranking

# Test URL
test_url = os.environ.get('KOL_SHEET_URL', 'https://docs.google.com/spreadsheets/d/1o6qMdV7bQ7ADDG8llRD1oy58iwfaa3mhFRR3DtsmutE/edit')
test_sheet = 'Sheet1'

print("=" * 60)
print("TEST 1: Lấy dữ liệu từ cache (nếu có)")
print("=" * 60)

cached_kols = get_kol_ranking_from_db(test_url, test_sheet)

if cached_kols:
    print(f"✅ Tìm thấy {len(cached_kols)} KOL trong cache")
    for kol in cached_kols[:3]:
        print(f"  - {kol['tiktok_account']}: Rank #{kol.get('rank', 'N/A')}, Score: {kol.get('kol_score', 0):.2f}")
        if kol.get('videos'):
            print(f"    Videos: {len(kol['videos'])} video(s)")
            for v in kol['videos'][:2]:
                days = v.get('days_since_posted', 'N/A')
                print(f"      • {days}d ago - {v.get('views', 0):,} views")
else:
    print("❌ Không có dữ liệu trong cache")
    print("   → Cần chạy API /api/kol/ranking để lấy dữ liệu mới")

print("\n" + "=" * 60)
print("TEST 2: Kiểm tra cấu trúc dữ liệu")
print("=" * 60)

if cached_kols and len(cached_kols) > 0:
    sample = cached_kols[0]
    print(f"Sample KOL: {sample['tiktok_account']}")
    print(f"  - Has total_stats: {bool(sample.get('total_stats'))}")
    print(f"  - Has videos: {bool(sample.get('videos'))}")
    print(f"  - Has rank: {bool(sample.get('rank'))}")
    print(f"  - Has kol_score: {bool(sample.get('kol_score'))}")
    
    if sample.get('videos'):
        video = sample['videos'][0]
        print(f"\n  Sample Video:")
        print(f"    - video_id: {video.get('video_id')}")
        print(f"    - posted_at: {video.get('posted_at')}")
        print(f"    - days_since_posted: {video.get('days_since_posted')}")
        print(f"    - views: {video.get('views', 0):,}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Sheet URL: {test_url[:50]}...")
print(f"Sheet Name: {test_sheet}")
print(f"Cached KOLs: {len(cached_kols) if cached_kols else 0}")
print("\nNếu không có dữ liệu, hãy:")
print("1. Mở frontend: http://localhost:3000/kol-management")
print("2. Click 'Tải bảng xếp hạng'")
print("3. Chạy lại script này")
