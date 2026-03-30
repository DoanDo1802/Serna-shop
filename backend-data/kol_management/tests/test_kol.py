"""
Script test hệ thống quản lý KOL
"""
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from kol_management.sheets_reader import read_kol_data_from_sheets
from kol_management.tiktok_stats import get_video_stats
from kol_management.kol_processor import process_kol_data, rank_kols_by_engagement

def test_read_sheets():
    """Test đọc dữ liệu từ Google Sheets"""
    print("\n=== TEST 1: Đọc dữ liệu từ Google Sheets ===")
    
    sheet_url = "https://docs.google.com/spreadsheets/d/1o6qMdV7bQ7ADDG8llRD1oy58iwfaa3mhFRR3DtsmutE/edit"
    
    try:
        kols = read_kol_data_from_sheets(sheet_url, "KOL_management")
        print(f"✅ Đã đọc {len(kols)} KOL")
        
        if kols:
            print("\n📋 Mẫu dữ liệu KOL đầu tiên:")
            kol = kols[0]
            print(f"  - TikTok Account: {kol['tiktok_account']}")
            print(f"  - TikTok Link: {kol['tiktok_link']}")
            print(f"  - Sản phẩm: {kol['product']}")
            print(f"  - Số bài đăng: {kol['post_count']}")
            if kol['post_links']:
                print(f"  - Link bài đăng:")
                for i, link in enumerate(kol['post_links'], 1):
                    print(f"    {i}. {link}")
        
        return True
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def test_video_stats():
    """Test lấy stats của một video"""
    print("\n=== TEST 2: Lấy stats video TikTok ===")
    
    # Thay bằng link video thật để test
    test_url = "https://www.tiktok.com/@cohocchamda/video/7458819473033989382"
    
    try:
        stats = get_video_stats(test_url)
        print(f"✅ Đã lấy stats cho video")
        print(f"  - Video ID: {stats.get('video_id')}")
        print(f"  - Likes: {stats.get('likes'):,}")
        print(f"  - Comments: {stats.get('comments'):,}")
        print(f"  - Shares: {stats.get('shares'):,}")
        print(f"  - Views: {stats.get('views'):,}")
        print(f"  - Engagement Rate: {stats.get('engagement_rate')}%")
        
        if 'error' in stats:
            print(f"⚠️ Có lỗi: {stats['error']}")
        
        return True
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def test_full_process():
    """Test toàn bộ quy trình: đọc sheets + lấy stats + xếp hạng"""
    print("\n=== TEST 3: Quy trình đầy đủ ===")
    
    sheet_url = "https://docs.google.com/spreadsheets/d/1o6qMdV7bQ7ADDG8llRD1oy58iwfaa3mhFRR3DtsmutE/edit"
    
    try:
        print("📊 Đang xử lý dữ liệu KOL...")
        kols = process_kol_data(sheet_url, "KOL_management")
        
        print(f"\n✅ Đã xử lý {len(kols)} KOL")
        
        print("\n🏆 Đang xếp hạng...")
        ranked = rank_kols_by_engagement(kols)
        
        print(f"\n📈 TOP 5 KOL theo Engagement:")
        for kol in ranked[:5]:
            stats = kol.get('total_stats', {})
            print(f"\n{kol['rank']}. {kol['tiktok_account']}")
            print(f"   - Sản phẩm: {kol['product']}")
            print(f"   - Số video: {kol['post_count']}")
            print(f"   - Tổng views: {stats.get('views', 0):,}")
            print(f"   - Tổng engagement: {stats.get('total_engagement', 0):,}")
            print(f"   - Avg engagement rate: {stats.get('avg_engagement_rate', 0)}%")
        
        return True
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 BẮT ĐẦU TEST HỆ THỐNG QUẢN LÝ KOL\n")
    
    # Test 1: Đọc sheets
    test1 = test_read_sheets()
    
    # Test 2: Lấy video stats (comment out nếu không muốn test)
    # test2 = test_video_stats()
    
    # Test 3: Quy trình đầy đủ (comment out nếu không muốn crawl nhiều video)
    # test3 = test_full_process()
    
    print("\n" + "="*50)
    print("KẾT QUẢ TEST:")
    print(f"  Test 1 (Đọc Sheets): {'✅ PASS' if test1 else '❌ FAIL'}")
    # print(f"  Test 2 (Video Stats): {'✅ PASS' if test2 else '❌ FAIL'}")
    # print(f"  Test 3 (Full Process): {'✅ PASS' if test3 else '❌ FAIL'}")
    print("="*50)
