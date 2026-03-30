# Logic Đồng Bộ KOL từ Google Sheets

## Tổng quan

Khi bạn click "Cập nhật từ TikTok", hệ thống sẽ:
1. ✅ **Thêm KOL mới** từ Sheets vào Database
2. ✅ **Cập nhật KOL cũ** với số liệu mới nhất
3. ✅ **Xóa KOL** không còn trong Sheets khỏi Database
4. ✅ **Cập nhật videos** (xóa videos cũ, thêm videos mới)

## Chi tiết Flow

### Scenario 1: Thêm KOL mới

```
Google Sheets:
- KOL A
- KOL B
- KOL C (MỚI THÊM)

Database trước khi sync:
- KOL A (rank: 1, score: 85)
- KOL B (rank: 2, score: 80)

↓ Click "Cập nhật từ TikTok"

Database sau khi sync:
- KOL A (rank: 1, score: 87) ← Cập nhật số liệu mới
- KOL B (rank: 2, score: 82) ← Cập nhật số liệu mới  
- KOL C (rank: 3, score: 75) ← THÊM MỚI
```

### Scenario 2: Xóa KOL

```
Google Sheets:
- KOL A
- KOL C
(Đã xóa KOL B)

Database trước khi sync:
- KOL A
- KOL B
- KOL C

↓ Click "Cập nhật từ TikTok"

Database sau khi sync:
- KOL A (cập nhật)
- KOL C (cập nhật)
(KOL B đã bị XÓA khỏi DB)
```

### Scenario 3: Thay đổi videos

```
Google Sheets - KOL A:
- Video 1 (cũ)
- Video 3 (mới thêm)
(Đã xóa Video 2)

Database trước khi sync - KOL A:
- Video 1 (1000 views)
- Video 2 (500 views)

↓ Click "Cập nhật từ TikTok"

Database sau khi sync - KOL A:
- Video 1 (1500 views) ← Cập nhật số liệu mới
- Video 3 (200 views) ← THÊM MỚI
(Video 2 đã bị XÓA)
```

## Code Logic

### 1. Xóa KOL không còn trong Sheets

```python
# Lấy danh sách KOL hiện tại từ Sheets
current_accounts = ['KOL_A', 'KOL_B', 'KOL_C']

# Lấy danh sách KOL trong DB
existing_kols = DB.get_kols(sheet_url, sheet_name)
# → ['KOL_A', 'KOL_B', 'KOL_D']

# Tìm KOL cần xóa
to_delete = ['KOL_D']  # Không còn trong Sheets

# Xóa khỏi DB
DB.delete('KOL_D')
```

### 2. Upsert KOL (Insert hoặc Update)

```python
for kol in sheets_kols:
    DB.upsert(kol)  # Tự động insert nếu mới, update nếu đã tồn tại
```

### 3. Refresh Videos

```python
# Xóa tất cả videos cũ của KOL
DB.delete_videos(kol_id)

# Insert videos mới từ Sheets
for video in kol.videos:
    DB.insert_video(video)
```

## Kết quả

### ✅ Điều gì sẽ xảy ra:

1. **Thêm KOL mới vào Sheets** → Tự động thêm vào DB
2. **Xóa KOL khỏi Sheets** → Tự động xóa khỏi DB
3. **Thêm video mới cho KOL** → Tự động thêm vào DB
4. **Xóa video khỏi Sheets** → Tự động xóa khỏi DB
5. **Số liệu thay đổi** (views, likes) → Tự động cập nhật

### ⚠️ Lưu ý:

- **Cascade Delete:** Khi xóa KOL, tất cả videos và stats của KOL đó cũng bị xóa (do foreign key constraint)
- **Unique Key:** KOL được định danh bởi `(tiktok_account, sheet_url, sheet_name)`
- **Video Refresh:** Mỗi lần sync, videos cũ bị xóa và thay bằng videos mới từ Sheets

## Testing

### Test Case 1: Thêm KOL mới

```bash
# 1. Sync lần đầu với 3 KOL
curl -X POST http://localhost:5000/api/kol/ranking \
  -H "Content-Type: application/json" \
  -d '{"spreadsheet_url": "...", "sheet_name": "Sheet1", "use_cache": false}'

# Kết quả: 3 KOL trong DB

# 2. Thêm 2 KOL mới vào Google Sheets

# 3. Sync lại
curl -X POST http://localhost:5000/api/kol/ranking \
  -H "Content-Type: application/json" \
  -d '{"spreadsheet_url": "...", "sheet_name": "Sheet1", "use_cache": false}'

# Kết quả: 5 KOL trong DB (3 cũ + 2 mới)
```

### Test Case 2: Xóa KOL

```bash
# 1. Có 5 KOL trong DB

# 2. Xóa 2 KOL khỏi Google Sheets

# 3. Sync lại
curl -X POST http://localhost:5000/api/kol/ranking \
  -H "Content-Type: application/json" \
  -d '{"spreadsheet_url": "...", "sheet_name": "Sheet1", "use_cache": false}'

# Kết quả: 3 KOL trong DB (2 KOL đã bị xóa)
# Console log: "🗑️ Đã xóa KOL không còn trong sheet: KOL_X"
```

## Best Practices

1. **Sync thường xuyên:** Mỗi ngày/tuần để đảm bảo dữ liệu đồng bộ
2. **Kiểm tra console log:** Xem KOL nào được thêm/xóa/cập nhật
3. **Backup trước khi xóa:** Nếu lo mất dữ liệu, export DB trước
4. **Test với sheet nhỏ:** Thử với 2-3 KOL trước khi sync sheet lớn

## Troubleshooting

### Vấn đề: KOL bị xóa nhầm
**Nguyên nhân:** Tên KOL trong Sheets khác với DB (viết hoa/thường, khoảng trắng)
**Giải pháp:** Đảm bảo `tiktok_account` trong Sheets giống y hệt trong DB

### Vấn đề: Videos không cập nhật
**Nguyên nhân:** Lỗi khi xóa videos cũ
**Giải pháp:** Check console log, có thể cần xóa thủ công:
```sql
DELETE FROM kol_videos WHERE kol_id = X;
```

### Vấn đề: Dữ liệu không đồng bộ
**Nguyên nhân:** Đang dùng cache (`use_cache: true`)
**Giải pháp:** Dùng `use_cache: false` để force refresh
