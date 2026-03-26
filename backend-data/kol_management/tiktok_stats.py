"""
Module lấy thống kê video TikTok
Hỗ trợ 2 phương pháp:
1. Qua n8n webhook (khuyến nghị)
2. Parse trực tiếp từ HTML (có thể bị block)
"""
import json
import re
import os
import requests
from typing import Dict, Any, Optional

def extract_video_id(video_url: str) -> Optional[str]:
    """Trích xuất video ID từ URL TikTok"""
    match = re.search(r'/video/(\d+)', video_url)
    return match.group(1) if match else None

def get_video_stats_via_n8n(video_url: str, n8n_webhook_url: str = None) -> Dict[str, Any]:
    """
    Lấy stats qua n8n webhook (KHUYẾN NGHỊ)
    
    Args:
        video_url: URL của video TikTok
        n8n_webhook_url: URL của n8n webhook (mặc định lấy từ env)
    
    Returns:
        Dict chứa: likes, comments, shares, views, engagement_rate
    """
    if not n8n_webhook_url:
        n8n_webhook_url = os.environ.get('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/tiktok-stats')
    
    video_id = extract_video_id(video_url)
    
    try:
        print(f"🔗 Gọi n8n webhook: {n8n_webhook_url}")
        
        response = requests.post(
            n8n_webhook_url,
            json={"url": video_url},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        stats = {
            'video_id': video_id or '',
            'video_url': video_url,
            'views': data.get('views', 0),
            'likes': data.get('like', 0) or data.get('likes', 0),
            'comments': data.get('comment', 0) or data.get('comments', 0),
            'shares': data.get('share', 0) or data.get('shares', 0),
            'saves': data.get('save', 0) or data.get('saves', 0),
            'follower': data.get('follower', 0) or data.get('FOLLOWER', 0),
            'author': data.get('author', ''),
            'description': data.get('description', ''),
            'date': int(data.get('date', 0)) if data.get('date') else 0,  # Convert to int
            'engagement_rate': 0.0,
            'total_engagement': 0
        }
        
        # Tính engagement rate: ER = (Like + Comment + Share + Save) / View × 100%
        if stats['views'] > 0:
            total_engagement = stats['likes'] + stats['comments'] + stats['shares'] + stats['saves']
            stats['total_engagement'] = total_engagement
            stats['engagement_rate'] = round((total_engagement / stats['views']) * 100, 2)
        else:
            stats['total_engagement'] = 0
            stats['engagement_rate'] = 0.0
        
        print(f"✅ n8n: {stats['views']:,} views, {stats['likes']:,} likes")
        return stats
        
    except requests.RequestException as e:
        print(f"❌ n8n webhook error: {e}")
        return {
            'error': f'n8n webhook error: {str(e)}',
            'video_id': video_id or '',
            'video_url': video_url,
            'views': 0,
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'saves': 0,
            'engagement_rate': 0.0
        }

def load_tiktok_cookies():
    """Load TikTok cookies từ file"""
    cookie_file = os.path.join(os.path.dirname(__file__), '..', 'tiktok', '.tiktok_cookie')
    if os.path.exists(cookie_file):
        try:
            with open(cookie_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except:
            pass
    return ""

def get_video_stats(video_url: str, use_n8n: bool = True) -> Dict[str, Any]:
    """
    Lấy thống kê của một video TikTok
    
    Args:
        video_url: URL của video TikTok
        use_n8n: Có sử dụng n8n webhook không (mặc định True)
    
    Returns:
        Dict chứa: likes, comments, shares, views, engagement_rate
    """
    # Thử n8n webhook trước (nếu enabled)
    if use_n8n:
        n8n_url = os.environ.get('N8N_WEBHOOK_URL')
        if n8n_url:
            stats = get_video_stats_via_n8n(video_url, n8n_url)
            if 'error' not in stats or stats.get('views', 0) > 0:
                return stats
            print("⚠️ n8n failed, fallback to direct parse...")
    
    # Fallback: Parse trực tiếp từ HTML
    video_id = extract_video_id(video_url)
    if not video_id:
        return {
            'error': 'Invalid video URL',
            'video_url': video_url,
            'video_id': '',
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'views': 0,
            'engagement_rate': 0.0
        }
    
    stats = {
        'video_id': video_id,
        'video_url': video_url,
        'likes': 0,
        'comments': 0,
        'shares': 0,
        'views': 0,
        'saves': 0,
        'engagement_rate': 0.0
    }
    
    try:
        # Load cookies
        cookie_string = load_tiktok_cookies()
        
        # Setup headers giống browser thật
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-Ch-Ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.tiktok.com/',
            'Origin': 'https://www.tiktok.com'
        }
        
        if cookie_string:
            headers['Cookie'] = cookie_string
        
        print(f"🔍 Đang lấy HTML: {video_url}")
        
        # Fetch HTML
        response = requests.get(video_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        html_content = response.text
        
        # Extract JSON từ __UNIVERSAL_DATA_FOR_REHYDRATION__
        regex = r'<script [^>]*id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>([\s\S]*?)</script>'
        match = re.search(regex, html_content, re.IGNORECASE)
        
        if match and match.group(1):
            try:
                json_str = match.group(1).strip()
                data = json.loads(json_str)
                
                # Parse theo cấu trúc: __DEFAULT_SCOPE__['webapp.video-detail'].itemInfo.itemStruct.stats
                default_scope = data.get('__DEFAULT_SCOPE__', {})
                
                # Try different paths
                item_info = None
                
                # Path 1: webapp.video-detail
                if 'webapp.video-detail' in default_scope:
                    item_info = default_scope['webapp.video-detail'].get('itemInfo', {}).get('itemStruct', {})
                
                # Path 2: webapp.item-detail  
                elif 'webapp.item-detail' in default_scope:
                    item_info = default_scope['webapp.item-detail'].get('itemInfo', {}).get('itemStruct', {})
                
                if item_info and 'stats' in item_info:
                    stats_data = item_info['stats']
                    
                    stats['views'] = stats_data.get('playCount', 0)
                    stats['likes'] = stats_data.get('diggCount', 0)
                    stats['comments'] = stats_data.get('commentCount', 0)
                    stats['shares'] = stats_data.get('shareCount', 0)
                    stats['saves'] = stats_data.get('collectCount', 0)
                    
                    # Tính engagement rate: ER = (Like + Comment + Share + Save) / View × 100%
                    if stats['views'] > 0:
                        total_engagement = stats['likes'] + stats['comments'] + stats['shares'] + stats['saves']
                        stats['engagement_rate'] = round((total_engagement / stats['views']) * 100, 2)
                    else:
                        stats['engagement_rate'] = 0.0
                    
                    print(f"✅ Thành công: {stats['views']:,} views, {stats['likes']:,} likes, {stats['comments']:,} comments")
                    return stats
                else:
                    print(f"⚠️ Không tìm thấy itemInfo.itemStruct.stats trong JSON")
                    stats['error'] = 'Stats not found in JSON structure'
                    
            except json.JSONDecodeError as e:
                print(f"❌ Lỗi parse JSON: {e}")
                stats['error'] = f'JSON parse error: {str(e)}'
        else:
            print(f"⚠️ Không tìm thấy __UNIVERSAL_DATA_FOR_REHYDRATION__ trong HTML")
            stats['error'] = '__UNIVERSAL_DATA_FOR_REHYDRATION__ not found'
            
    except requests.RequestException as e:
        print(f"❌ Lỗi request: {e}")
        stats['error'] = f'Request error: {str(e)}'
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        stats['error'] = str(e)
    
    return stats

if __name__ == "__main__":
    # Test với video từ danh sách KOL
    test_urls = [
        "https://www.tiktok.com/@dimkhongquao/video/7579969522069785874",
        "https://www.tiktok.com/@chanhocts1/video/7611209758455909640",
    ]
    
    for test_url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {test_url}")
        print('='*60)
        stats = get_video_stats(test_url)
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        print()
