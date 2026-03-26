"""
Module tính điểm video và xếp hạng KOL
Theo thiết kế: backend-data/kolrank.md
"""
import math
import time
from typing import List, Dict, Any

# Constants
DAYS_THRESHOLD = 90  # Chỉ lấy video trong 3 tháng gần nhất
K_ADJUSTMENT = 50  # Hệ số điều chỉnh ER
MIN_VIEWS_THRESHOLD = 50  # Lọc video có views quá thấp
CONFIDENCE_THRESHOLD = 5000  # Views cần để đạt confidence = 1 (tăng từ 1000 → 5000)
FRESHNESS_DECAY = 60  # Hệ số decay sau 30 ngày (càng lớn càng giảm chậm)
VIRAL_ALPHA = 0.4  # Độ mạnh của viral boost (0.3 - 0.5)
VIRAL_BETA_MIN = 100  # Giá trị tối thiểu của beta
VIRAL_BETA_RATIO = 0.05  # Tỷ lệ follower để tính beta
VIRAL_BOOST_CAP = 2.0  # Cap viral boost tối đa


def filter_recent_videos(videos: List[Dict[str, Any]], days: int = DAYS_THRESHOLD) -> List[Dict[str, Any]]:
    """
    Lọc video trong N ngày gần nhất
    
    Args:
        videos: List video stats
        days: Số ngày (mặc định 90 = 3 tháng)
    
    Returns:
        List video đã lọc
    """
    current_time = int(time.time())
    filtered = []
    
    for video in videos:
        # Bỏ qua video có lỗi hoặc views quá thấp
        if video.get('error') or video.get('views', 0) < MIN_VIEWS_THRESHOLD:
            continue
        
        # Kiểm tra thời gian
        video_date = video.get('date', 0)
        
        # Convert to int if string
        if isinstance(video_date, str):
            try:
                video_date = int(video_date)
            except (ValueError, TypeError):
                video_date = 0
        
        # Nếu không có date, vẫn cho vào nhưng set age = 90 (cũ nhất)
        if video_date == 0:
            video['age_in_days'] = days  # Set to max age
            filtered.append(video)
            continue
            
        age_in_days = (current_time - video_date) / 86400
        
        if age_in_days <= days:
            video['age_in_days'] = age_in_days
            filtered.append(video)
    
    return filtered


def calculate_freshness(age_in_days: float) -> float:
    """
    Tính độ mới của video (IMPROVED)
    
    Công thức:
    - Video 0-3 ngày: freshness = 0.8 (cho cơ hội nhưng chưa trust tuyệt đối)
    - Video 3-14 ngày: freshness = 1.0 (đang viral, trust tối đa)
    - Video 14-30 ngày: freshness = 0.9 (đã xác thực, giảm nhẹ)
    - Video 30-90 ngày: freshness giảm dần theo e^(-(age - 30) / 60)
    
    Ví dụ:
    - Video 1-3 ngày: freshness = 0.8 (80% - cho cơ hội detect viral)
    - Video 3-14 ngày: freshness = 1.0 (100% - peak viral window)
    - Video 14-30 ngày: freshness = 0.9 (90% - đã xác thực)
    - Video 40 ngày: freshness ≈ 0.77 (77%)
    - Video 60 ngày: freshness ≈ 0.55 (55%)
    - Video 90 ngày: freshness ≈ 0.33 (33%)
    """
    if age_in_days <= 3:
        # Video mới, cho cơ hội nhưng chưa trust tuyệt đối
        return 0.8
    elif age_in_days <= 14:
        # Peak viral window (24-72h đầu là lúc detect viral)
        return 1.0
    elif age_in_days <= 30:
        # Đã xác thực, giảm nhẹ
        return 0.9
    else:
        # Sau 30 ngày, bắt đầu decay (chậm hơn với hệ số 60)
        return math.exp(-(age_in_days - 30) / FRESHNESS_DECAY)


def calculate_adjusted_er(total_engagement: int, views: int, k: int = K_ADJUSTMENT) -> float:
    """
    Tính Adjusted Engagement Rate
    adjusted_ER = (total_engagement + k) / (views + k)
    
    Tránh ER bị ảo khi views thấp
    """
    return (total_engagement + k) / (views + k)


def calculate_confidence(views: int, threshold: int = CONFIDENCE_THRESHOLD) -> float:
    """
    Tính độ tin cậy dựa trên views (IMPROVED)
    confidence = min(1, views / threshold)
    
    - views >= 5000: confidence = 1.0 (full trust)
    - views = 2500: confidence = 0.5
    - views = 1000: confidence = 0.2
    - views = 500: confidence = 0.1
    
    Alternative (smooth): min(1, log10(views + 1) / 4)
    """
    return min(1.0, views / threshold)


def calculate_scaled_views(views: int) -> float:
    """
    Scale views bằng log để giảm bias
    scaled_views = log10(views + 1)
    """
    return math.log10(views + 1)


def calculate_viral_boost(views: int, follower: int) -> float:
    """
    Tính viral boost - khả năng viral vượt follower (cân bằng + capped)
    
    viral_boost = min(2.0, 1 + α × log₁₀(views / (follower + β) + 1))
    
    Với:
    - α = 0.4 (độ mạnh của boost)
    - β = max(100, follower × 0.05) (đệm để tránh bias)
    - Cap tối đa = 2.0 (tránh extreme cases)
    
    Ví dụ:
    - KOL nhỏ (100 follower), 10K views:
      β = max(100, 5) = 100
      boost = min(2.0, 1 + 0.4 × log₁₀(10000/200 + 1)) = min(2.0, 1.68) = 1.68
    
    - KOL lớn (100K follower), 1M views:
      β = max(100, 5000) = 5000
      boost = min(2.0, 1 + 0.4 × log₁₀(1000000/105000 + 1)) = min(2.0, 1.40) = 1.40
    
    - Video viral extreme (100 follower, 1M views):
      β = 100
      boost = min(2.0, 1 + 0.4 × log₁₀(1000000/200 + 1)) = min(2.0, 2.48) = 2.0 (capped)
    
    Lợi ích:
    - Không bias KOL nhỏ (có β đệm)
    - Không giết KOL lớn (β scale theo follower)
    - Cap mềm tránh extreme cases
    - Boost chỉ là signal phụ (1.0 - 2.0 range)
    """
    beta = max(VIRAL_BETA_MIN, follower * VIRAL_BETA_RATIO)
    viral_ratio = views / (follower + beta)
    boost = 1 + VIRAL_ALPHA * math.log10(viral_ratio + 1)
    return min(VIRAL_BOOST_CAP, boost)


def calculate_video_score(video: Dict[str, Any]) -> float:
    """
    Tính điểm cho một video
    
    video_score = scaled_views × adjusted_ER × confidence × freshness × viral_boost × 100
    (Nhân 100 để score dễ đọc hơn)
    
    Args:
        video: Dict chứa stats của video
    
    Returns:
        Video score
    """
    views = video.get('views', 0)
    total_engagement = video.get('total_engagement', 0)
    follower = video.get('follower', 1)
    age_in_days = video.get('age_in_days', 0)
    
    # Tính các thành phần
    scaled_views = calculate_scaled_views(views)
    adjusted_er = calculate_adjusted_er(total_engagement, views)
    confidence = calculate_confidence(views)
    freshness = calculate_freshness(age_in_days)
    viral_boost = calculate_viral_boost(views, follower)
    
    # Tính score (nhân 100 để dễ đọc)
    score = scaled_views * adjusted_er * confidence * freshness * viral_boost * 100
    
    # Lưu các thành phần để debug
    video['scoring_components'] = {
        'scaled_views': round(scaled_views, 2),
        'adjusted_er': round(adjusted_er, 4),
        'confidence': round(confidence, 2),
        'freshness': round(freshness, 4),
        'viral_boost': round(viral_boost, 2),
        'score': round(score, 2)
    }
    
    return score


def calculate_kol_score_weighted(videos: List[Dict[str, Any]]) -> float:
    """
    Tính KOL score bằng trung bình có trọng số (IMPROVED)
    
    KOL_score = weighted_avg(video_score)
    weight = log10(views + 1) × confidence
    
    Cải tiến: Nhân thêm confidence để giảm bias từ video nhiều views nhưng chưa ổn định
    
    Args:
        videos: List video đã có score
    
    Returns:
        KOL score
    """
    if not videos:
        return 0.0
    
    total_weighted_score = 0.0
    total_weight = 0.0
    
    for video in videos:
        score = video.get('scoring_components', {}).get('score', 0)
        confidence = video.get('scoring_components', {}).get('confidence', 1.0)
        weight = math.log10(video.get('views', 0) + 1) * confidence
        
        total_weighted_score += score * weight
        total_weight += weight
    
    if total_weight == 0:
        return 0.0
    
    return total_weighted_score / total_weight


def calculate_kol_score_top_n(videos: List[Dict[str, Any]], n: int = 5) -> float:
    """
    Tính KOL score bằng trung bình top N video gần nhất
    
    Args:
        videos: List video đã có score
        n: Số video lấy (mặc định 5)
    
    Returns:
        KOL score
    """
    if not videos:
        return 0.0
    
    # Sắp xếp theo thời gian (mới nhất trước)
    sorted_videos = sorted(videos, key=lambda x: x.get('date', 0), reverse=True)
    
    # Lấy top N
    top_videos = sorted_videos[:n]
    
    # Tính trung bình score
    scores = [v.get('scoring_components', {}).get('score', 0) for v in top_videos]
    
    return sum(scores) / len(scores) if scores else 0.0


def score_kol_videos(kol: Dict[str, Any], method: str = 'weighted') -> Dict[str, Any]:
    """
    Tính điểm cho tất cả video của KOL và tính KOL score
    
    Args:
        kol: Dict chứa thông tin KOL và videos
        method: 'weighted' hoặc 'top_n'
    
    Returns:
        KOL dict đã được enrich với scores
    """
    videos = kol.get('videos', [])
    kol_name = kol.get('tiktok_account', 'Unknown')
    
    if not videos:
        print(f"⚠️ {kol_name}: Không có video")
        kol['kol_score'] = 0.0
        kol['scored_videos'] = []
        return kol
    
    print(f"\n📊 Đang tính điểm cho {kol_name}...")
    
    # Filter video trong 3 tháng gần nhất
    recent_videos = filter_recent_videos(videos)
    
    if not recent_videos:
        print(f"⚠️ {kol_name}: Không có video trong 3 tháng gần nhất")
        kol['kol_score'] = 0.0
        kol['scored_videos'] = []
        return kol
    
    print(f"  ✅ Tìm thấy {len(recent_videos)} video trong 3 tháng gần nhất")
    
    # Tính score cho từng video
    for i, video in enumerate(recent_videos, 1):
        score = calculate_video_score(video)
        components = video.get('scoring_components', {})
        print(f"  📹 Video {i}: score={components.get('score', 0):.2f} "
              f"(views={video.get('views', 0):,}, ER={video.get('engagement_rate', 0):.1f}%, "
              f"age={video.get('age_in_days', 0):.0f}d)")
    
    # Tính KOL score
    if method == 'weighted':
        kol['kol_score'] = calculate_kol_score_weighted(recent_videos)
        print(f"  🏆 KOL Score (weighted): {kol['kol_score']:.2f}")
    else:
        kol['kol_score'] = calculate_kol_score_top_n(recent_videos)
        print(f"  🏆 KOL Score (top_n): {kol['kol_score']:.2f}")
    
    kol['scored_videos'] = recent_videos
    kol['total_scored_videos'] = len(recent_videos)
    
    return kol


def rank_kols_by_score(kols: List[Dict[str, Any]], method: str = 'weighted') -> List[Dict[str, Any]]:
    """
    Xếp hạng KOL theo score
    
    Args:
        kols: List KOL
        method: 'weighted' hoặc 'top_n'
    
    Returns:
        List KOL đã xếp hạng
    """
    print("\n" + "=" * 60)
    print("🏆 BẮT ĐẦU TÍNH ĐIỂM VÀ XẾP HẠNG KOL")
    print("=" * 60)
    
    # Tính score cho từng KOL
    for kol in kols:
        score_kol_videos(kol, method)
    
    # Sắp xếp theo KOL Score
    ranked = sorted(kols, key=lambda x: x.get('kol_score', 0), reverse=True)
    
    # Thêm rank
    print("\n" + "=" * 60)
    print("📊 KẾT QUẢ XẾP HẠNG")
    print("=" * 60)
    
    for i, kol in enumerate(ranked, 1):
        kol['rank'] = i
        score = kol.get('kol_score', 0)
        videos_count = kol.get('total_scored_videos', 0)
        print(f"#{i} {kol.get('tiktok_account', 'Unknown')}: {score:.2f} điểm ({videos_count} videos)")
    
    print("=" * 60 + "\n")
    
    return ranked


if __name__ == "__main__":
    # Test với dữ liệu mẫu
    test_video = {
        "views": 563500,
        "likes": 83600,
        "comments": 893,
        "shares": 19100,
        "saves": 7713,
        "follower": 847,
        "video_id": "7611209758455909640",
        "author": "chanhocts1",
        "description": "đoán vội flop #onthihsg #toan #hoctap #viraltiktok #dongluc",
        "error": "",
        "date": 1772122871,
        "engagement_rate": 19.75,
        "total_engagement": 111306
    }
    
    # Tính age
    current_time = int(time.time())
    test_video['age_in_days'] = (current_time - test_video['date']) / 86400
    
    # Tính score
    score = calculate_video_score(test_video)
    
    print("=" * 60)
    print("TEST VIDEO SCORING")
    print("=" * 60)
    print(f"Video: {test_video['video_id']}")
    print(f"Views: {test_video['views']:,}")
    print(f"Total Engagement: {test_video['total_engagement']:,}")
    print(f"Follower: {test_video['follower']}")
    print(f"Age: {test_video['age_in_days']:.1f} days")
    print()
    print("Scoring Components:")
    for key, value in test_video['scoring_components'].items():
        print(f"  {key}: {value}")
    print()
    print(f"Final Score: {score:.2f}")
    print("=" * 60)
