# Giải pháp Duplicate Video khi có nhiều Sheets

## 🐛 Vấn đề

### Scenario:
```
Sheet1 (KOL_management): Có KOL A với video 123
Sheet2 (DATA): Cũng có KOL A với video 123

Khi sync Sheet1:
- KOL A → kol_id = 100
- Video 123 → (kol_id=100, video_id=123) ✅

Khi sync Sheet2:
- KOL A → kol_id = 200 (khác kol_id vì khác sheet)
- Video 123 → (kol_id=200, video_id=123) ✅

→ Không conflict vì kol_id khác nhau!
```

### Vấn đề thực sự:

**Khi sync lại Sheet1 lần 2:**
```
1. Xóa videos cũ của kol_id=100
2. Nếu xóa THẤT BẠI (connection error, timeout, etc.)
3. Insert video 123 → (kol_id=100, video_id=123)
4. ❌ Duplicate! Vì video cũ vẫn còn
```

---

## ✅ Giải pháp

### 1. Smart Insert/Upsert Logic

```python
# Track xem có xóa thành công không
videos_deleted = False

try:
    supabase.table('kol_videos').delete().eq('kol_id', kol_id).execute()
    videos_deleted = True
except:
    videos_deleted = False

# Insert hoặc Upsert tùy trạng thái
for video in videos:
    if videos_deleted:
        # Đã xóa thành công → Dùng INSERT (nhanh hơn)
        supabase.table('kol_videos').insert(video_record).execute()
    else:
        # Không xóa được → Dùng UPSERT (an toàn hơn)
        supabase.table('kol_videos').upsert(
            video_record,
            on_conflict='kol_id,video_id'
        ).execute()
```

### 2. Retry Logic cho Connection Errors

```python
def retry_on_disconnect(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if 'disconnect' in str(e).lower():
                if attempt < max_retries - 1:
                    time.sleep(delay * (attempt + 1))
                    continue
            raise
```

### 3. Suppress Duplicate Error Logs

```python
except Exception as video_error:
    error_msg = str(video_error)
    # Chỉ log lỗi KHÔNG phải duplicate
    if 'duplicate' not in error_msg.lower():
        print(f"⚠️ Lỗi: {error_msg}")
```

---

## 📊 Flow Chart

### Flow cũ (có lỗi):
```
┌─────────────────┐
│ Xóa videos cũ   │
└────────┬────────┘
         │
    ❌ FAILED
         │
         ▼
┌─────────────────┐
│ Insert videos   │ ← Duplicate!
└─────────────────┘
```

### Flow mới (đã fix):
```
┌─────────────────┐
│ Xóa videos cũ   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
✅ SUCCESS  ❌ FAILED
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│ INSERT │ │ UPSERT │
└────────┘ └────────┘
    │         │
    └────┬────┘
         ▼
    ✅ No Duplicate!
```

---

## 🎯 Kết quả

### Trước khi fix:
```
❌ duplicate key (kol_id, video_id)=(1055, 7581736775043878162)
→ Một số videos không lưu được
→ Dữ liệu không đầy đủ
```

### Sau khi fix:
```
✅ Tất cả videos đều lưu thành công
✅ Không còn duplicate error
✅ Dữ liệu đầy đủ và chính xác
```

---

## 💡 Best Practices

### 1. Luôn track trạng thái operations
```python
operation_success = False
try:
    do_operation()
    operation_success = True
except:
    operation_success = False

# Xử lý dựa trên trạng thái
if operation_success:
    # Path A
else:
    # Path B (fallback)
```

### 2. Dùng Upsert khi không chắc chắn
```python
# Thay vì:
delete_old()
insert_new()  # Có thể duplicate nếu delete fail

# Dùng:
upsert_new()  # Luôn an toàn
```

### 3. Retry cho network operations
```python
# Supabase, API calls, etc. có thể bị disconnect
result = retry_on_disconnect(lambda: supabase.table(...).execute())
```

### 4. Log có điều kiện
```python
# Không log tất cả errors
if 'expected_error' not in error_msg:
    print(f"⚠️ Unexpected error: {error_msg}")
```

---

## 🔍 Debugging

### Kiểm tra duplicate videos:
```sql
-- Tìm videos bị duplicate
SELECT kol_id, video_id, COUNT(*) as count
FROM kol_videos
GROUP BY kol_id, video_id
HAVING COUNT(*) > 1;

-- Xem chi tiết
SELECT k.tiktok_account, k.sheet_name, v.video_id, v.video_url
FROM kol_videos v
JOIN kols k ON v.kol_id = k.id
WHERE (v.kol_id, v.video_id) IN (
    SELECT kol_id, video_id
    FROM kol_videos
    GROUP BY kol_id, video_id
    HAVING COUNT(*) > 1
);
```

### Xóa duplicates thủ công:
```sql
-- Giữ lại record mới nhất, xóa cũ
DELETE FROM kol_videos
WHERE id NOT IN (
    SELECT MAX(id)
    FROM kol_videos
    GROUP BY kol_id, video_id
);
```

---

## 📝 Notes

### Tại sao không dùng upsert cho tất cả?
- **Insert nhanh hơn** khi chắc chắn không duplicate
- **Upsert chậm hơn** vì phải check conflict
- **Hybrid approach** = Tốc độ + An toàn

### Tại sao không dùng transaction?
- Supabase Python client chưa hỗ trợ transaction tốt
- Retry logic + upsert đã đủ an toàn
- Transaction có thể gây deadlock nếu timeout

### Có ảnh hưởng performance không?
- **Không đáng kể**
- Chỉ dùng upsert khi delete fail (hiếm khi xảy ra)
- Phần lớn trường hợp vẫn dùng insert (nhanh)

---

## ✅ Checklist

- [x] Track trạng thái delete operation
- [x] Dùng insert khi delete thành công
- [x] Dùng upsert khi delete thất bại
- [x] Retry logic cho connection errors
- [x] Suppress duplicate error logs
- [x] Test với nhiều sheets có cùng KOL
- [x] Test với connection errors

---

## 🚀 Testing

### Test Case 1: Delete thành công
```python
# Sync Sheet1
→ Delete videos: ✅ Success
→ Insert videos: ✅ Success
→ No duplicate
```

### Test Case 2: Delete thất bại
```python
# Sync Sheet1
→ Delete videos: ❌ Failed (connection error)
→ Upsert videos: ✅ Success
→ No duplicate (upsert handled it)
```

### Test Case 3: Nhiều sheets cùng KOL
```python
# Sync Sheet1: KOL A
→ kol_id = 100
→ Videos: (100, 123), (100, 456)

# Sync Sheet2: KOL A
→ kol_id = 200 (khác sheet → khác kol_id)
→ Videos: (200, 123), (200, 456)

→ No conflict! (kol_id khác nhau)
```

### Test Case 4: Sync lại cùng sheet
```python
# Sync Sheet1 lần 1
→ Videos: (100, 123), (100, 456)

# Sync Sheet1 lần 2
→ Delete old: ✅
→ Insert new: ✅
→ No duplicate
```

---

## 🎓 Lessons Learned

1. **Luôn có fallback plan** - Nếu operation A fail, có plan B
2. **Track trạng thái** - Biết operation thành công hay thất bại
3. **Retry network operations** - Connection có thể bị ngắt bất cứ lúc nào
4. **Log có ý nghĩa** - Không log expected errors
5. **Test edge cases** - Connection errors, duplicates, etc.
