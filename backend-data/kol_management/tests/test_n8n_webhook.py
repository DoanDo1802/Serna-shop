"""
Test n8n webhook integration
"""
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from kol_management.tiktok_stats import get_video_stats_via_n8n

def test_n8n_webhook():
    """Test n8n webhook với một video"""
    
    # Test URLs
    test_urls = [
        "https://www.tiktok.com/@dimkhongquao/video/7579969522069785874",
        "https://www.tiktok.com/@chanhocts1/video/7611209758455909640",
    ]
    
    # n8n webhook URL (có thể override bằng env var)
    n8n_url = os.environ.get('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/tiktok-stats')
    
    print("="*70)
    print("TEST N8N WEBHOOK INTEGRATION")
    print("="*70)
    print(f"\nn8n Webhook URL: {n8n_url}\n")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/{len(test_urls)}: {url}")
        print('='*70)
        
        try:
            stats = get_video_stats_via_n8n(url, n8n_url)
            
            print("\n📊 KẾT QUẢ:")
            print(json.dumps(stats, indent=2, ensure_ascii=False))
            
            if 'error' in stats:
                print(f"\n⚠️ Có lỗi: {stats['error']}")
            elif stats.get('views', 0) > 0:
                print(f"\n✅ THÀNH CÔNG!")
                print(f"   Views: {stats['views']:,}")
                print(f"   Likes: {stats['likes']:,}")
                print(f"   Comments: {stats['comments']:,}")
                print(f"   Shares: {stats['shares']:,}")
                print(f"   Engagement Rate: {stats['engagement_rate']}%")
            else:
                print(f"\n❌ THẤT BẠI - Không lấy được stats")
                
        except Exception as e:
            print(f"\n❌ LỖI: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("HOÀN THÀNH TEST")
    print("="*70)

if __name__ == "__main__":
    test_n8n_webhook()
