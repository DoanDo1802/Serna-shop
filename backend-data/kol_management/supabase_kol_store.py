"""
Module lưu trữ dữ liệu KOL vào Supabase
"""
import os
import time
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from datetime import datetime

# Khởi tạo Supabase client
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def retry_on_disconnect(func, max_retries=3, delay=1):
    """
    Retry function nếu gặp lỗi Server disconnected
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_msg = str(e).lower()
            if 'disconnect' in error_msg or 'connection' in error_msg:
                if attempt < max_retries - 1:
                    print(f"⚠️ Connection error, retry {attempt + 1}/{max_retries}...")
                    time.sleep(delay * (attempt + 1))  # Exponential backoff
                    continue
            raise  # Re-raise nếu không phải connection error hoặc hết retries
    raise Exception("Max retries exceeded")


def save_kol_ranking(
    kols: List[Dict[str, Any]], 
    sheet_url: str, 
    sheet_name: str
) -> Dict[str, Any]:
    """
    Lưu dữ liệu KOL ranking vào Supabase
    
    Args:
        kols: List các KOL với đầy đủ thông tin (rank, stats, videos)
        sheet_url: URL của Google Sheet
        sheet_name: Tên sheet
    
    Returns:
        Dict với thông tin kết quả
    """
    try:
        saved_kols = 0
        saved_videos = 0
        
        # Lấy danh sách tiktok_account từ sheet hiện tại
        current_accounts = [kol['tiktok_account'] for kol in kols]
        
        # Xóa các KOL không còn trong sheet (đã bị xóa khỏi Google Sheets)
        try:
            existing_kols = supabase.table('kols')\
                .select('id, tiktok_account')\
                .eq('sheet_url', sheet_url)\
                .eq('sheet_name', sheet_name)\
                .execute()
            
            if existing_kols.data:
                for existing in existing_kols.data:
                    if existing['tiktok_account'] not in current_accounts:
                        # KOL này đã bị xóa khỏi sheet, xóa khỏi DB
                        supabase.table('kols').delete().eq('id', existing['id']).execute()
                        print(f"🗑️  Đã xóa KOL không còn trong sheet: {existing['tiktok_account']}")
        except Exception as e:
            print(f"⚠️ Không thể kiểm tra KOL cũ: {e}")
        
        # Upsert các KOL từ sheet
        for kol_data in kols:
            # 1. Upsert KOL
            kol_record = {
                'tiktok_account': kol_data['tiktok_account'],
                'tiktok_link': kol_data['tiktok_link'],
                'product': kol_data.get('product', ''),
                'sheet_url': sheet_url,
                'sheet_name': sheet_name,
                'post_count': kol_data.get('post_count', 0),
                'rank': kol_data.get('rank'),
                'kol_score': kol_data.get('kol_score'),
                'total_scored_videos': kol_data.get('total_scored_videos', 0),
            }
            
            # Upsert KOL (insert or update)
            result = retry_on_disconnect(
                lambda: supabase.table('kols').upsert(
                    kol_record,
                    on_conflict='tiktok_account,sheet_url,sheet_name'
                ).execute()
            )
            
            if result.data:
                kol_id = result.data[0]['id']
                saved_kols += 1
                
                # 2. Upsert Total Stats
                if 'total_stats' in kol_data and kol_data['total_stats']:
                    stats = kol_data['total_stats']
                    stats_record = {
                        'kol_id': kol_id,
                        'total_likes': stats.get('likes', 0),
                        'total_comments': stats.get('comments', 0),
                        'total_shares': stats.get('shares', 0),
                        'total_views': stats.get('views', 0),
                        'total_engagement': stats.get('total_engagement', 0),
                        'avg_engagement_rate': stats.get('avg_engagement_rate', 0),
                    }
                    
                    retry_on_disconnect(
                        lambda: supabase.table('kol_total_stats').upsert(
                            stats_record,
                            on_conflict='kol_id'
                        ).execute()
                    )
                
                # 3. Xóa videos cũ của KOL này trước khi thêm mới
                # (Để tránh videos cũ không còn trong sheet vẫn nằm trong DB)
                videos_deleted = False
                try:
                    delete_result = retry_on_disconnect(
                        lambda: supabase.table('kol_videos').delete().eq('kol_id', kol_id).execute()
                    )
                    videos_deleted = True
                    if delete_result.data:
                        print(f"🗑️  Đã xóa {len(delete_result.data)} video cũ của KOL {kol_data['tiktok_account']}")
                except Exception as del_error:
                    print(f"⚠️ Không thể xóa videos cũ: {del_error}")
                    # Nếu không xóa được, sẽ dùng upsert thay vì insert
                
                # 4. Insert/Upsert Videos mới
                if 'videos' in kol_data and kol_data['videos']:
                    for idx, video in enumerate(kol_data['videos']):
                        # Skip video có lỗi hoặc không có video_id
                        if video.get('error'):
                            continue
                        
                        video_id = video.get('video_id', '').strip()
                        video_url = video.get('video_url', '').strip()
                        
                        # Skip nếu không có video_id hoặc video_url
                        if not video_id or not video_url:
                            print(f"⚠️ Bỏ qua video không có ID: {video_url[:50] if video_url else 'N/A'}")
                            continue
                            
                        video_record = {
                            'kol_id': kol_id,
                            'video_id': video_id,
                            'video_url': video_url,
                            'likes': video.get('likes', 0),
                            'comments': video.get('comments', 0),
                            'shares': video.get('shares', 0),
                            'views': video.get('views', 0),
                            'engagement_rate': video.get('engagement_rate', 0),
                            'posted_at': video.get('posted_at'),  # ISO format timestamp
                            # days_since_posted sẽ tự động tính bởi trigger
                        }
                        
                        try:
                            if videos_deleted:
                                # Đã xóa thành công → Dùng insert
                                retry_on_disconnect(
                                    lambda: supabase.table('kol_videos').insert(video_record).execute()
                                )
                            else:
                                # Không xóa được → Dùng upsert để tránh duplicate
                                retry_on_disconnect(
                                    lambda: supabase.table('kol_videos').upsert(
                                        video_record,
                                        on_conflict='kol_id,video_id'
                                    ).execute()
                                )
                            saved_videos += 1
                        except Exception as video_error:
                            error_msg = str(video_error)
                            # Chỉ log lỗi không phải duplicate
                            if 'duplicate' not in error_msg.lower():
                                print(f"⚠️ Lỗi lưu video {video_id}: {error_msg}")
                            continue
        
        print(f"✅ Đã lưu {saved_kols} KOL và {saved_videos} video vào Supabase")
        
        return {
            'success': True,
            'saved_kols': saved_kols,
            'saved_videos': saved_videos
        }
        
    except Exception as e:
        print(f"❌ Lỗi lưu dữ liệu vào Supabase: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


def get_kol_ranking_from_db(
    sheet_url: str, 
    sheet_name: str
) -> List[Dict[str, Any]]:
    """
    Lấy dữ liệu KOL ranking từ Supabase
    
    Args:
        sheet_url: URL của Google Sheet
        sheet_name: Tên sheet
    
    Returns:
        List các KOL với đầy đủ thông tin
    """
    try:
        # Lấy KOLs với stats
        result = supabase.table('kols')\
            .select('*, kol_total_stats(*), kol_videos(*)')\
            .eq('sheet_url', sheet_url)\
            .eq('sheet_name', sheet_name)\
            .order('rank', desc=False)\
            .execute()
        
        if not result.data:
            return []
        
        # Format lại data
        kols = []
        for row in result.data:
            kol = {
                'tiktok_account': row['tiktok_account'],
                'tiktok_link': row['tiktok_link'],
                'product': row['product'],
                'post_count': row['post_count'],
                'rank': row['rank'],
                'kol_score': row['kol_score'],
                'total_scored_videos': row['total_scored_videos'],
            }
            
            # Add total stats
            if row.get('kol_total_stats'):
                stats = row['kol_total_stats'][0] if isinstance(row['kol_total_stats'], list) else row['kol_total_stats']
                kol['total_stats'] = {
                    'likes': stats['total_likes'],
                    'comments': stats['total_comments'],
                    'shares': stats['total_shares'],
                    'views': stats['total_views'],
                    'total_engagement': stats['total_engagement'],
                    'avg_engagement_rate': stats['avg_engagement_rate'],
                }
            
            # Add videos
            if row.get('kol_videos'):
                videos = row['kol_videos'] if isinstance(row['kol_videos'], list) else [row['kol_videos']]
                kol['videos'] = []
                for v in videos:
                    kol['videos'].append({
                        'video_id': v['video_id'],
                        'video_url': v['video_url'],
                        'likes': v['likes'],
                        'comments': v['comments'],
                        'shares': v['shares'],
                        'views': v['views'],
                        'engagement_rate': v['engagement_rate'],
                        'posted_at': v['posted_at'],
                        'days_since_posted': v['days_since_posted'],
                    })
            
            kols.append(kol)
        
        print(f"✅ Đã lấy {len(kols)} KOL từ Supabase")
        return kols
        
    except Exception as e:
        print(f"❌ Lỗi lấy dữ liệu từ Supabase: {e}")
        return []


def delete_kol_data(sheet_url: str, sheet_name: str) -> Dict[str, Any]:
    """
    Xóa tất cả dữ liệu KOL của một sheet
    
    Args:
        sheet_url: URL của Google Sheet
        sheet_name: Tên sheet
    
    Returns:
        Dict với thông tin kết quả
    """
    try:
        result = supabase.table('kols')\
            .delete()\
            .eq('sheet_url', sheet_url)\
            .eq('sheet_name', sheet_name)\
            .execute()
        
        print(f"✅ Đã xóa dữ liệu KOL của sheet: {sheet_name}")
        
        return {
            'success': True,
            'deleted_count': len(result.data) if result.data else 0
        }
        
    except Exception as e:
        print(f"❌ Lỗi xóa dữ liệu: {e}")
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    # Test
    print("Testing Supabase KOL Store...")
    
    # Test get data
    test_url = "https://docs.google.com/spreadsheets/d/1o6qMdV7bQ7ADDG8llRD1oy58iwfaa3mhFRR3DtsmutE/edit"
    kols = get_kol_ranking_from_db(test_url, "KOL_management")
    print(f"Found {len(kols)} KOLs in database")
