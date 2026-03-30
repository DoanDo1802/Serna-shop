# 🏆 Hệ thống Chấm điểm KOL - Tóm tắt

## 📊 Tổng quan

Xếp hạng KOL dựa trên **hiệu suất video trong 3 tháng gần nhất**, đánh giá toàn diện:

```
KOL Score = Trung bình có trọng số của tất cả video
```

---

## 🎯 Công thức Chấm điểm

### Bước 1: Tính điểm từng video

```
Video Score = Views × ER × Độ mới × Viral × Độ tin cậy
```

**5 yếu tố chính:**

1. **Views (Lượt xem)** - Độ phủ sóng
   - Dùng log để cân bằng (10K views ≠ gấp 10 lần 1K views)

2. **ER (Engagement Rate)** - Chất lượng tương tác
   - ER = (Likes + Comments + Shares + Saves) / Views × 100%
   - ER cao = nội dung hấp dẫn

3. **Độ mới (Freshness)** - Ưu tiên video gần đây
   - Video 3-14 ngày: 100% (peak viral)
   - Video 1-3 ngày: 80% (đang viral)
   - Video > 30 ngày: giảm dần

4. **Viral** - Khả năng vượt follower
   - Video có views cao so với follower → bonus
   - Tối đa gấp 2 lần (tránh extreme cases)

5. **Độ tin cậy (Confidence)** - Dựa trên views
   - ≥ 5K views: 100% tin cậy
   - < 5K views: giảm tỷ lệ

---

### Bước 2: Tính điểm KOL

```
KOL Score = Trung bình có trọng số
```

**Trọng số:**
- Video nhiều views + tin cậy cao → trọng số lớn
- Video ít views → trọng số nhỏ

---

## 📈 Ví dụ Minh họa

### KOL A: 2 videos

**Video 1:**
- 1,584 views, ER 8.7%, 81 ngày tuổi
- Score: **16.36**

**Video 2:**
- 3,529 views, ER 5.8%, 79 ngày tuổi
- Score: **11.88**

**KOL Score:**
```
Video 2 có views cao hơn → trọng số lớn hơn
→ KOL Score = 14.00
```

---

## ✅ Ưu điểm Hệ thống

### 1. Công bằng
- KOL nhỏ có ER cao vẫn có cơ hội
- Không bị "auto win" bởi views lớn

### 2. Toàn diện
- Không chỉ xem views
- Đánh giá cả chất lượng (ER), độ mới, viral

### 3. Chống gian lận
- Video ít views bị giảm trọng số
- Viral boost có giới hạn
- ER được điều chỉnh tránh ảo

### 4. Ưu tiên video mới
- Video gần đây được đánh giá cao hơn
- Phản ánh hiệu suất hiện tại

---

## 🎯 Kết luận

**Hệ thống đánh giá KOL dựa trên:**

✅ **Performance** (Views + ER)  
✅ **Quality** (Engagement thực tế)  
✅ **Recency** (Video mới quan trọng hơn)  
✅ **Viral Potential** (Khả năng vượt follower)  
✅ **Reliability** (Độ tin cậy dựa trên views)

→ **Kết quả:** Xếp hạng công bằng, toàn diện, khó gian lận

---

## 📊 So sánh với Phương pháp Cũ

| Tiêu chí | Cũ | Mới |
|----------|-----|-----|
| Đánh giá | Chỉ tổng engagement | 5 yếu tố toàn diện |
| Công bằng | KOL lớn auto win | Cân bằng lớn/nhỏ |
| Video mới | Không ưu tiên | Ưu tiên cao |
| Chống gian lận | Yếu | Mạnh (nhiều cơ chế) |
| Viral | Không đo | Có đo + giới hạn |

---

## 🚀 Triển khai

- **Backend:** Python (video_scoring.py)
- **Frontend:** React/Next.js
- **API:** REST API
- **Data:** Google Sheets + TikTok API

**Thời gian xử lý:** ~30s cho 10 KOL (tùy số video)
