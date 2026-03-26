"""
Module xử lý và enrich dữ liệu KOL
"""
from typing import List, Dict, Any
from .sheets_reader import read_kol_data_from_sheets
from .tiktok_stats import get_video_stats
from .video_scoring import rank_kols_by_score

def process_kol_data(spreadsheet_url: str, sheet_name: str = "KOL_management") -> List[Dict[str, Any]]:
    """
    Đọc dữ liệu KOL từ Sheets và enrich với stats từ TikTok
    
    Args:
        spreadsheet_url: URL của Google Sheet
        sheet_name: Tên sheet
    
    Returns:
        List KOL đã được enrich với video stats
    """
    # Đọc dữ liệu từ Sheets
    kols = read_kol_data_from_sheets(spreadsheet_url, sheet_name)
    
    # Enrich với video stats
    for kol in kols:
        if kol['post_links']:
            print(f"\n🔍 Đang lấy stats cho {kol['tiktok_account']} ({len(kol['post_links'])} videos)...")
            video_stats = []
            
            for link in kol['post_links']:
                try:
                    stats = get_video_stats(link)
                    video_stats.append(stats)
                    
                    # Hiển thị kết quả
                    if 'error' not in stats or stats.get('views', 0) > 0:
                        print(f"  ✅ {stats.get('views', 0):,} views, {stats.get('likes', 0):,} likes")
                    else:
                        print(f"  ⚠️ Không lấy được stats: {stats.get('error', 'Unknown error')}")
                except Exception as e:
                    print(f"  ❌ Lỗi: {e}")
                    video_stats.append({
                        'video_url': link,
                        'likes': 0,
                        'comments': 0,
                        'shares': 0,
                        'views': 0,
                        'engagement_rate': 0,
                        'error': str(e)
                    })
            
            kol['videos'] = video_stats
            
            # Tính tổng engagement (chỉ tính video có data)
            valid_videos = [v for v in video_stats if v.get('views', 0) > 0]
            
            if valid_videos:
                total_likes = sum(v.get('likes', 0) for v in valid_videos)
                total_comments = sum(v.get('comments', 0) for v in valid_videos)
                total_shares = sum(v.get('shares', 0) for v in valid_videos)
                total_saves = sum(v.get('saves', 0) for v in valid_videos)
                total_views = sum(v.get('views', 0) for v in valid_videos)
                
                # Tính tổng engagement: Like + Comment + Share + Save
                total_engagement = total_likes + total_comments + total_shares + total_saves
                
                # Tính avg engagement rate: ER = Total Engagement / Total Views × 100%
                avg_engagement_rate = round((total_engagement / total_views * 100), 2) if total_views > 0 else 0.0
                
                kol['total_stats'] = {
                    'likes': total_likes,
                    'comments': total_comments,
                    'shares': total_shares,
                    'saves': total_saves,
                    'views': total_views,
                    'total_engagement': total_engagement,
                    'avg_engagement_rate': avg_engagement_rate
                }
                print(f"  📊 Tổng: {total_views:,} views, {total_likes:,} likes, engagement: {kol['total_stats']['total_engagement']:,}")
            else:
                kol['total_stats'] = {
                    'likes': 0,
                    'comments': 0,
                    'shares': 0,
                    'views': 0,
                    'total_engagement': 0,
                    'avg_engagement_rate': 0
                }
                print(f"  ⚠️ Không có video nào có stats hợp lệ")
        else:
            kol['videos'] = []
            kol['total_stats'] = {
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'saves': 0,
                'views': 0,
                'total_engagement': 0,
                'avg_engagement_rate': 0.0
            }
    
    return kols

def rank_kols_by_engagement(kols: List[Dict[str, Any]], method: str = 'weighted') -> List[Dict[str, Any]]:
    """
    Xếp hạng KOL theo video scoring system
    
    Sử dụng công thức phức tạp:
    - Filter video trong 3 tháng gần nhất
    - Tính video_score = scaled_views × adjusted_ER × confidence × freshness × viral_boost
    - Tính KOL_score = weighted_avg(video_score) hoặc avg(top N)
    
    Args:
        kols: List KOL đã có stats
        method: 'weighted' (khuyến nghị) hoặc 'top_n'
    
    Returns:
        List KOL đã được sắp xếp theo kol_score giảm dần
    """
    return rank_kols_by_score(kols, method)

if __name__ == "__main__":
    # Test
    test_url = "https://docs.google.com/spreadsheets/d/1o6qMdV7bQ7ADDG8llRD1oy58iwfaa3mhFRR3DtsmutE/edit"
    kols = process_kol_data(test_url)
    ranked = rank_kols_by_engagement(kols, method='weighted')
    
    print("\n🏆 TOP 5 KOL (theo Video Scoring System):")
    for kol in ranked[:5]:
        kol_score = kol.get('kol_score', 0)
        total_videos = kol.get('total_scored_videos', 0)
        print(f"{kol['rank']}. {kol['tiktok_account']}: KOL Score = {kol_score:.2f} ({total_videos} videos trong 3 tháng)")
