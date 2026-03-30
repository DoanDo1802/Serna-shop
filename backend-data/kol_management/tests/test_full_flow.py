"""
Test toàn bộ flow: Google Sheets → n8n → Ranking
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from kol_management.kol_processor import process_kol_data, rank_kols_by_engagement

def test_full_flow():
    sheet_url = 'https://docs.google.com/spreadsheets/d/1o6qMdV7bQ7ADDG8llRD1oy58iwfaa3mhFRR3DtsmutE/edit'
    
    print('🚀 BẮT ĐẦU XỬ LÝ DỮ LIỆU KOL')
    print('='*70)
    print()
    
    # Lấy dữ liệu
    print('📊 Đang lấy dữ liệu từ Google Sheets...')
    kols = process_kol_data(sheet_url, 'KOL_management')
    
    # Giới hạn 3 KOL đầu để test nhanh
    print(f'\n⚠️ Test mode: Chỉ xử lý 3 KOL đầu tiên (tổng: {len(kols)} KOL)')
    kols = kols[:3]
    
    print('\n🏆 Đang xếp hạng...')
    ranked = rank_kols_by_engagement(kols)
    
    print()
    print('='*70)
    print('📈 TOP 3 KOL:')
    print('='*70)
    
    for kol in ranked:
        stats = kol.get('total_stats', {})
        print(f"""
{kol['rank']}. {kol['tiktok_account']}
   Sản phẩm: {kol['product']}
   Số video: {kol['post_count']}
   Views: {stats.get('views', 0):,}
   Likes: {stats.get('likes', 0):,}
   Comments: {stats.get('comments', 0):,}
   Shares: {stats.get('shares', 0):,}
   Total Engagement: {stats.get('total_engagement', 0):,}
   Avg Engagement Rate: {stats.get('avg_engagement_rate', 0)}%
""")
    
    print('='*70)
    print('✅ HOÀN THÀNH!')

if __name__ == "__main__":
    test_full_flow()
