# 📅 Hiển thị Thời gian Đăng Video

## Tổng quan

Cột "Thời gian đăng" trong bảng xếp hạng hiển thị số ngày kể từ khi mỗi video được đăng.

---

## 🎨 Cách hiển thị

### Ví dụ 1: KOL có 1 video
```
┌─────────────────┐
│ Thời gian đăng  │
├─────────────────┤
│     [19d]       │
└─────────────────┘
```

### Ví dụ 2: KOL có 2 videos
```
┌─────────────────┐
│ Thời gian đăng  │
├─────────────────┤
│  [12d] [30d]    │
└─────────────────┘
```

### Ví dụ 3: KOL có 3 videos
```
┌─────────────────┐
│ Thời gian đăng  │
├─────────────────┤
│ [5d] [12d] [30d]│
└─────────────────┘
```

### Ví dụ 4: KOL có nhiều videos
```
┌──────────────────────────┐
│    Thời gian đăng        │
├──────────────────────────┤
│ [3d] [7d] [12d] [19d]    │
│ [25d] [30d]              │
└──────────────────────────┘
```

---

## ✨ Tính năng

### 1. Sắp xếp tự động
- Videos được sắp xếp từ **mới nhất → cũ nhất**
- Video đăng gần đây nhất ở đầu tiên

**Ví dụ:**
```
Videos: 30d, 12d, 5d
→ Hiển thị: [5d] [12d] [30d]
```

### 2. Tooltip (Hover để xem)
- Di chuột vào badge để xem chi tiết
- Hiển thị: "Video 1: 5 ngày trước"

### 3. Badge màu
- Màu xám nhạt (secondary)
- Font monospace để dễ đọc
- Kích thước nhỏ (text-xs)

### 4. Responsive
- Tự động xuống dòng nếu quá nhiều videos
- Không bị tràn ra ngoài cell

---

## 📊 Ý nghĩa

### Video mới (< 7 ngày)
```
[3d] [5d] [6d]
```
- ✅ KOL đang active
- ✅ Nội dung mới, có thể đang viral
- ✅ Đáng theo dõi

### Video trung bình (7-30 ngày)
```
[12d] [19d] [25d]
```
- 👍 Đã qua peak viral window
- 👍 Số liệu đã ổn định
- 👍 Đánh giá chính xác hơn

### Video cũ (> 30 ngày)
```
[45d] [60d] [80d]
```
- ⚠️ KOL ít đăng bài
- ⚠️ Dữ liệu có thể lỗi thời
- ⚠️ Cần cập nhật

---

## 🎯 Use Cases

### Case 1: Đánh giá tần suất đăng bài

**KOL A:**
```
[2d] [5d] [8d] [12d]
```
→ Đăng đều, 2-3 ngày/video → ✅ Active

**KOL B:**
```
[45d] [60d]
```
→ Lâu không đăng → ⚠️ Không active

---

### Case 2: Phát hiện video viral

**KOL C:**
```
[3d] [7d] [30d]
```
→ Video 3d có thể đang viral → 🔥 Quan tâm

---

### Case 3: Đánh giá độ tin cậy

**KOL D:**
```
[15d] [20d] [25d]
```
→ Tất cả video đã qua 14 ngày → ✅ Dữ liệu đáng tin

**KOL E:**
```
[1d] [2d] [3d]
```
→ Tất cả video mới → ⚠️ Chưa ổn định, cần đợi

---

## 🔧 Technical Details

### Data Source
```typescript
interface VideoStats {
  video_id: string
  video_url: string
  posted_at?: string        // ISO timestamp
  days_since_posted?: number // Tự động tính từ posted_at
  // ... other stats
}
```

### Calculation
```sql
-- Trigger tự động tính trong Supabase
CREATE TRIGGER calc_days_since_posted
BEFORE INSERT OR UPDATE ON kol_videos
FOR EACH ROW
EXECUTE FUNCTION calculate_days_since_posted();

-- Function
CREATE OR REPLACE FUNCTION calculate_days_since_posted()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.posted_at IS NOT NULL THEN
        NEW.days_since_posted = EXTRACT(DAY FROM (NOW() - NEW.posted_at))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';
```

### Frontend Display
```tsx
{kol.videos
  .filter(video => video.days_since_posted !== undefined)
  .sort((a, b) => (a.days_since_posted || 0) - (b.days_since_posted || 0))
  .map((video, idx) => (
    <Badge 
      key={idx} 
      variant="secondary" 
      className="text-xs font-mono"
      title={`Video ${idx + 1}: ${video.days_since_posted} ngày trước`}
    >
      {video.days_since_posted}d
    </Badge>
  ))
}
```

---

## 📈 Ví dụ Thực tế

### KOL: @dimkhongquao
```
Videos: 2
Thời gian: [12d] [19d]
```

**Phân tích:**
- 2 videos trong 19 ngày
- Tần suất: ~1 video/tuần
- Video mới nhất: 12 ngày trước
- → Đánh giá: Active vừa phải

---

### KOL: @chanhocts1
```
Videos: 3
Thời gian: [5d] [15d] [30d]
```

**Phân tích:**
- 3 videos trong 30 ngày
- Tần suất: ~1 video/10 ngày
- Video mới nhất: 5 ngày trước
- → Đánh giá: Active tốt

---

## 💡 Tips

### Tip 1: Xem nhanh KOL active
```
Tìm KOL có badge [Xd] với X < 7
→ KOL đang active, đăng bài thường xuyên
```

### Tip 2: Phát hiện video viral
```
Video mới (< 7d) + Views cao + ER cao
→ Có thể đang viral
```

### Tip 3: Đánh giá độ tin cậy
```
Tất cả videos > 14d
→ Dữ liệu đã ổn định, đáng tin cậy
```

### Tip 4: Cảnh báo KOL không active
```
Tất cả videos > 30d
→ KOL lâu không đăng, cần cập nhật hoặc loại bỏ
```

---

## 🎨 UI/UX

### Màu sắc
- **Badge:** Xám nhạt (secondary)
- **Text:** Đen (dark mode: trắng)
- **Font:** Monospace (dễ đọc số)

### Kích thước
- **Badge:** text-xs (12px)
- **Gap:** 4px giữa các badge
- **Padding:** 2px 6px

### Hover Effect
- Hiển thị tooltip với thông tin chi tiết
- Không có animation (giữ đơn giản)

---

## 🔄 Auto-update

### Cách hoạt động:
1. Khi lưu video vào DB, `posted_at` được lưu (ISO format)
2. Trigger tự động tính `days_since_posted`
3. Mỗi ngày, `days_since_posted` tự động tăng lên 1

### Ví dụ:
```
Ngày 1: Video đăng → days_since_posted = 0
Ngày 2: Auto update → days_since_posted = 1
Ngày 3: Auto update → days_since_posted = 2
...
```

**Lưu ý:** Cần chạy "Cập nhật từ TikTok" để refresh `days_since_posted` mới nhất!

---

## ✅ Checklist

- [x] Hiển thị tất cả videos
- [x] Sắp xếp từ mới → cũ
- [x] Tooltip khi hover
- [x] Responsive (tự động xuống dòng)
- [x] Font monospace dễ đọc
- [x] Auto-calculate từ posted_at
- [x] Update mỗi ngày

---

## 🚀 Future Enhancements

### Có thể thêm:
1. **Màu theo độ mới:**
   - < 7d: Xanh lá (mới)
   - 7-30d: Xám (bình thường)
   - > 30d: Đỏ (cũ)

2. **Click để xem video:**
   - Click badge → Mở video TikTok

3. **Thống kê:**
   - Hiển thị "Trung bình: 15d"
   - Hiển thị "Tần suất: 1 video/tuần"

4. **Filter:**
   - Lọc KOL có video < 7d
   - Lọc KOL có video > 30d
