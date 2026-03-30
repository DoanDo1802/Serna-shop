# Hướng dẫn Setup Supabase cho KOL Management

## 1. Tạo Database Tables

Truy cập Supabase Dashboard → SQL Editor và chạy file schema:

```bash
# Copy nội dung file này và paste vào SQL Editor
backend-data/kol_management/supabase_kol_schema.sql
```

Hoặc chạy từng bước:

### Bước 1: Tạo bảng `kols`
```sql
CREATE TABLE IF NOT EXISTS kols (
    id SERIAL PRIMARY KEY,
    tiktok_account TEXT NOT NULL,
    tiktok_link TEXT NOT NULL,
    product TEXT,
    sheet_url TEXT NOT NULL,
    sheet_name TEXT NOT NULL,
    post_count INTEGER DEFAULT 0,
    rank INTEGER,
    kol_score NUMERIC,
    total_scored_videos INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_kol_per_sheet UNIQUE (tiktok_account, sheet_url, sheet_name)
);
```

### Bước 2: Tạo bảng `kol_videos`
```sql
CREATE TABLE IF NOT EXISTS kol_videos (
    id SERIAL PRIMARY KEY,
    kol_id INTEGER NOT NULL REFERENCES kols(id) ON DELETE CASCADE,
    video_id TEXT NOT NULL,
    video_url TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    engagement_rate NUMERIC DEFAULT 0,
    posted_at TIMESTAMPTZ,
    days_since_posted INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_video_per_kol UNIQUE (kol_id, video_id)
);
```

### Bước 3: Tạo bảng `kol_total_stats`
```sql
CREATE TABLE IF NOT EXISTS kol_total_stats (
    id SERIAL PRIMARY KEY,
    kol_id INTEGER NOT NULL REFERENCES kols(id) ON DELETE CASCADE,
    total_likes INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    total_shares INTEGER DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    total_engagement INTEGER DEFAULT 0,
    avg_engagement_rate NUMERIC DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_stats_per_kol UNIQUE (kol_id)
);
```

## 2. Cấu hình Environment Variables

Thêm vào file `.env`:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
```

Lấy thông tin từ:
- Supabase Dashboard → Settings → API
- URL: Project URL
- Key: service_role key (không phải anon key!)

## 3. Cài đặt Python Package

```bash
pip install supabase
```

## 4. Cấu trúc Database

### Bảng `kols`
Lưu thông tin cơ bản của KOL:
- `tiktok_account`: Tên TikTok
- `tiktok_link`: Link profile
- `product`: Sản phẩm quảng cáo
- `rank`: Thứ hạng
- `kol_score`: Điểm đánh giá
- `sheet_url`, `sheet_name`: Nguồn dữ liệu

### Bảng `kol_videos`
Lưu thông tin từng video:
- `video_id`, `video_url`: ID và link video
- `likes`, `comments`, `shares`, `views`: Metrics
- `engagement_rate`: Tỷ lệ tương tác
- `posted_at`: Thời gian đăng (ISO format)
- `days_since_posted`: Số ngày kể từ khi đăng (tự động tính)

### Bảng `kol_total_stats`
Tổng hợp stats của KOL:
- `total_likes`, `total_comments`, `total_shares`, `total_views`
- `total_engagement`: Tổng tương tác
- `avg_engagement_rate`: ER trung bình

## 5. Tính năng

### Auto-cache
- Khi gọi API `/api/kol/ranking`, dữ liệu tự động lưu vào Supabase
- Lần sau F5 sẽ load từ cache (nhanh hơn)
- Muốn refresh: gọi với `use_cache: false`

### Auto-calculate days_since_posted
- Trigger tự động tính số ngày từ `posted_at`
- Hiển thị dạng "12d", "5d" trên UI

### Unique constraints
- Mỗi KOL chỉ có 1 record cho mỗi sheet
- Mỗi video chỉ có 1 record cho mỗi KOL
- Tự động update nếu đã tồn tại (upsert)

## 6. API Usage

### Lấy ranking (có cache)
```python
POST /api/kol/ranking
{
  "spreadsheet_url": "https://docs.google.com/...",
  "sheet_name": "KOL_management",
  "use_cache": true  // Mặc định true
}
```

### Lấy ranking (force refresh)
```python
POST /api/kol/ranking
{
  "spreadsheet_url": "https://docs.google.com/...",
  "sheet_name": "KOL_management",
  "use_cache": false  // Bỏ qua cache, lấy mới từ TikTok
}
```

## 7. Testing

```bash
# Test Supabase connection
cd backend-data/kol_management
python3 supabase_kol_store.py

# Test full flow
python3 test_full_flow.py
```

## 8. Troubleshooting

### Lỗi: "Missing SUPABASE_URL or SUPABASE_KEY"
→ Kiểm tra file `.env` có đầy đủ thông tin chưa

### Lỗi: "relation does not exist"
→ Chưa chạy schema SQL, quay lại bước 1

### Lỗi: "permission denied"
→ Đang dùng anon key thay vì service_role key

### Dữ liệu không update
→ Check unique constraints, có thể cần xóa dữ liệu cũ:
```sql
DELETE FROM kols WHERE sheet_url = 'your-sheet-url';
```

## 9. View Data

### Xem tất cả KOL
```sql
SELECT * FROM kol_full_details ORDER BY rank;
```

### Xem KOL của một sheet
```sql
SELECT * FROM get_kol_ranking(
  'https://docs.google.com/spreadsheets/d/...',
  'KOL_management'
);
```

### Xem videos của một KOL
```sql
SELECT * FROM kol_videos 
WHERE kol_id = 1 
ORDER BY posted_at DESC;
```
