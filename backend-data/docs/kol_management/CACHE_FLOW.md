# KOL Ranking Cache Flow

## Tổng quan

Hệ thống tự động lưu và load dữ liệu KOL từ Supabase để tránh mất dữ liệu khi F5.

## Flow hoạt động

### 1. Lần đầu tiên (Chưa có cache)

```
User mở trang → Không có dữ liệu
↓
User click "Tải bảng xếp hạng"
↓
Backend lấy dữ liệu từ TikTok (qua n8n)
↓
Backend tính toán ranking
↓
Backend LƯU vào Supabase (tự động)
↓
Frontend hiển thị kết quả
```

### 2. Lần sau (Đã có cache)

```
User mở trang / F5
↓
Frontend TỰ ĐỘNG gọi API với use_cache=true
↓
Backend kiểm tra Supabase
↓
Có dữ liệu → Trả về ngay (nhanh!)
↓
Frontend hiển thị kết quả
```

### 3. Cập nhật dữ liệu mới

```
User click "Cập nhật từ TikTok"
↓
Frontend gọi API với use_cache=false
↓
Backend BỎ QUA cache
↓
Backend lấy dữ liệu mới từ TikTok
↓
Backend CẬP NHẬT Supabase (upsert)
↓
Frontend hiển thị kết quả mới
```

## Buttons trên UI

### "Làm mới" (Refresh)
- Chỉ hiện khi đã có dữ liệu
- Load lại từ cache (nhanh)
- `use_cache = true`

### "Tải bảng xếp hạng" / "Cập nhật từ TikTok"
- "Tải bảng xếp hạng": Khi chưa có dữ liệu
- "Cập nhật từ TikTok": Khi đã có dữ liệu
- Lấy dữ liệu mới từ TikTok (chậm hơn)
- `use_cache = false`

## Database Behavior

### Upsert Logic
```sql
-- Khi save_kol_ranking() được gọi:
INSERT INTO kols (tiktok_account, sheet_url, sheet_name, ...)
VALUES (...)
ON CONFLICT (tiktok_account, sheet_url, sheet_name)
DO UPDATE SET
  rank = EXCLUDED.rank,
  kol_score = EXCLUDED.kol_score,
  updated_at = NOW()
```

### Kết quả:
- Lần 1: Tạo mới record
- Lần 2+: Cập nhật record cũ (KHÔNG tạo duplicate)
- Videos cũng được upsert tương tự

## Auto-calculate Features

### days_since_posted
```sql
-- Trigger tự động tính khi insert/update
CREATE TRIGGER calc_days_since_posted
BEFORE INSERT OR UPDATE ON kol_videos
FOR EACH ROW
EXECUTE FUNCTION calculate_days_since_posted();
```

Kết quả:
- `posted_at = "2024-03-14T10:00:00Z"`
- `days_since_posted = 12` (tự động tính)
- UI hiển thị: "12d"

## Testing

### Test cache flow:
```bash
cd backend-data/kol_management
python3 test_cache_flow.py
```

### Test full flow:
```bash
python3 test_full_flow.py
```

## Troubleshooting

### Vấn đề: F5 không thấy dữ liệu
**Nguyên nhân:** Frontend chưa auto-load từ cache
**Giải pháp:** Đã fix bằng useEffect hook

### Vấn đề: Dữ liệu bị duplicate
**Nguyên nhân:** Unique constraint không hoạt động
**Giải pháp:** Kiểm tra constraint trong Supabase:
```sql
SELECT * FROM kols 
WHERE tiktok_account = 'test_account'
AND sheet_url = 'your_url';
```

### Vấn đề: days_since_posted không tự động tính
**Nguyên nhân:** Trigger chưa được tạo
**Giải pháp:** Chạy lại schema SQL:
```sql
CREATE TRIGGER calc_days_since_posted
BEFORE INSERT OR UPDATE ON kol_videos
FOR EACH ROW
EXECUTE FUNCTION calculate_days_since_posted();
```

## Performance

### Load từ cache (use_cache=true):
- Thời gian: ~200-500ms
- Không cần gọi TikTok API
- Không cần tính toán ranking

### Load mới (use_cache=false):
- Thời gian: ~30-60 giây (tùy số KOL)
- Gọi TikTok API cho mỗi video
- Tính toán ranking
- Lưu vào Supabase

## Best Practices

1. **Lần đầu setup:** Click "Tải bảng xếp hạng" để tạo cache
2. **Xem dữ liệu:** F5 trang → Tự động load từ cache
3. **Cập nhật định kỳ:** Click "Cập nhật từ TikTok" mỗi ngày/tuần
4. **Nhiều sheet:** Mỗi sheet có cache riêng (theo sheet_url + sheet_name)

## API Response

### Có cache:
```json
{
  "success": true,
  "ranking": [...],
  "total": 10,
  "from_cache": true
}
```

### Không có cache:
```json
{
  "success": true,
  "ranking": [...],
  "total": 10,
  "from_cache": false
}
```
