-- Migration: Thêm cột total_videos vào bảng kols
-- Chạy script này trong Supabase SQL Editor

-- 1. Thêm cột total_videos
ALTER TABLE kols 
ADD COLUMN IF NOT EXISTS total_videos INTEGER DEFAULT 0;

-- 2. Cập nhật giá trị total_videos từ số lượng video hiện có
UPDATE kols k
SET total_videos = (
    SELECT COUNT(*) 
    FROM kol_videos v 
    WHERE v.kol_id = k.id 
      AND v.video_id IS NOT NULL 
      AND v.video_id != ''
)
WHERE total_videos = 0;

-- 3. Thêm comment
COMMENT ON COLUMN kols.total_videos IS 'Tổng số video (bao gồm cả video cũ hơn 90 ngày)';

-- 4. Kiểm tra kết quả
SELECT 
    tiktok_account,
    total_scored_videos as videos_90d,
    total_videos as total_videos,
    kol_score
FROM kols
ORDER BY rank ASC NULLS LAST
LIMIT 10;
