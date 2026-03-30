# Fix Video Count & Ranking Issues

## Vấn đề đã sửa

### 1. Video count hiển thị sai
**Trước:**
- Chỉ hiển thị số video trong 90 ngày (`total_scored_videos`)
- KOL có video cũ hơn 90 ngày bị hiển thị là "0 video"

**Sau:**
- Hiển thị cả 2 số: `Videos (90d/Tổng)`
- Ví dụ: `3/5` = 3 video trong 90 ngày được tính điểm, 5 video tổng cộng
- KOL có video cũ vẫn hiển thị đúng số lượng

### 2. Ranking sai
**Trước:**
- KOL có video cũ (>90 ngày) có `kol_score = 0`
- Bị xếp hạng xuống dưới cùng với KOL không có video

**Sau:**
- Ranking ưu tiên theo `kol_score` (giảm dần)
- KOL có cùng score sẽ được xếp theo `total_videos` (nhiều video hơn = xếp trên)
- KOL có video cũ vẫn được xếp hạng đúng

### 3. Logic tính điểm
**Không thay đổi:**
- Chỉ video trong 90 ngày mới được tính điểm
- Video cũ hơn 90 ngày: `kol_score = 0` nhưng vẫn hiển thị số lượng

**Lý do:**
- Video cũ không còn giá trị viral/engagement cao
- Nhưng vẫn cần hiển thị để biết KOL có hoạt động hay không

## Cách cập nhật

### Bước 1: Cập nhật Database Schema
Chạy migration SQL trong Supabase SQL Editor:

```bash
# File: backend-data/kol_management/migration_add_total_videos.sql
```

Hoặc chạy trực tiếp:

```sql
ALTER TABLE kols 
ADD COLUMN IF NOT EXISTS total_videos INTEGER DEFAULT 0;

UPDATE kols k
SET total_videos = (
    SELECT COUNT(*) 
    FROM kol_videos v 
    WHERE v.kol_id = k.id 
      AND v.video_id IS NOT NULL 
      AND v.video_id != ''
)
WHERE total_videos = 0;
```

### Bước 2: Restart Backend
```bash
cd backend-data
# Nếu đang chạy, stop và restart
python app.py
```

### Bước 3: Refresh Frontend
```bash
cd frontend-base
npm run dev
```

### Bước 4: Cập nhật dữ liệu
1. Vào trang KOL Management
2. Click "Cập nhật từ TikTok" để lấy dữ liệu mới
3. Dữ liệu sẽ được lưu với cột `total_videos` mới

## Kiểm tra kết quả

### Trong Database (Supabase SQL Editor):
```sql
SELECT 
    tiktok_account,
    rank,
    kol_score,
    total_scored_videos as videos_90d,
    total_videos,
    CASE 
        WHEN total_videos > total_scored_videos 
        THEN 'Có video cũ'
        ELSE 'Tất cả video mới'
    END as status
FROM kols
ORDER BY rank ASC NULLS LAST;
```

### Trong Frontend:
- Cột "Videos (90d/Tổng)" hiển thị 2 số
- KOL có video cũ hiển thị: `3` (90d) và `/5 tổng` (màu xám)
- KOL chỉ có video mới hiển thị: `5` (outline badge)

## Ví dụ

### Case 1: KOL có video mới
```
Rank: #1
Videos: 5 (outline badge)
Score: 125.50
→ Tất cả 5 video đều trong 90 ngày
```

### Case 2: KOL có video cũ
```
Rank: #5
Videos: 3 (default badge)
        /8 tổng (outline badge, màu xám)
Score: 45.20
→ 3 video trong 90 ngày được tính điểm
→ 5 video cũ hơn 90 ngày không tính điểm
```

### Case 3: KOL chỉ có video cũ
```
Rank: #15
Videos: 0 (default badge)
        /3 tổng (outline badge, màu xám)
Score: 0.00
→ Không có video trong 90 ngày
→ 3 video cũ hơn 90 ngày
→ Vẫn được xếp hạng (không bị ẩn)
```

## Technical Details

### Backend Changes
1. `video_scoring.py`:
   - Thêm `total_videos` vào kết quả scoring
   - Cải thiện ranking: sort theo `(kol_score, total_videos)`
   - Log rõ hơn: hiển thị `X/Y videos được tính điểm`

2. `supabase_kol_store.py`:
   - Lưu `total_videos` vào database
   - Đọc `total_videos` khi query

3. `supabase_kol_schema.sql`:
   - Thêm cột `total_videos INTEGER DEFAULT 0`
   - Comment: "Tổng số video (bao gồm cả video cũ)"

### Frontend Changes
1. `lib/api.ts`:
   - Thêm `total_videos?: number` vào interface `KOL`

2. `app/kol-management/page.tsx`:
   - Đổi header: "Videos" → "Videos (90d/Tổng)"
   - Logic hiển thị:
     - Nếu `total_videos > total_scored_videos`: hiển thị 2 badge
     - Nếu bằng nhau: hiển thị 1 badge outline

## Troubleshooting

### Vấn đề: Vẫn hiển thị sai sau khi update
**Giải pháp:**
1. Clear cache browser (Ctrl+Shift+R)
2. Kiểm tra database đã có cột `total_videos` chưa
3. Click "Cập nhật từ TikTok" để refresh dữ liệu

### Vấn đề: Ranking vẫn sai
**Giải pháp:**
1. Kiểm tra `kol_score` trong database
2. Đảm bảo đã restart backend
3. Click "Cập nhật từ TikTok" để tính lại ranking

### Vấn đề: Migration SQL lỗi
**Giải pháp:**
```sql
-- Kiểm tra cột đã tồn tại chưa
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'kols' 
  AND column_name = 'total_videos';

-- Nếu chưa có, chạy lại:
ALTER TABLE kols ADD COLUMN total_videos INTEGER DEFAULT 0;
```

## Notes

- Video cũ hơn 90 ngày vẫn được lưu trong database
- Chỉ không tính điểm, không phải xóa
- Giúp theo dõi lịch sử hoạt động của KOL
- Ranking công bằng hơn: KOL có video cũ không bị đẩy xuống dưới cùng
