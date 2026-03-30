# 🎯 Ngưỡng Điểm KOL - Khuyến nghị Hợp tác

## 📊 Phân tích Thang điểm

Dựa trên công thức tính điểm hiện tại, KOL Score có thể dao động từ **0 đến ~100+**

### Các yếu tố ảnh hưởng:
- **Scaled Views:** log₁₀(views + 1) → 0-6 (thực tế 2-5)
- **Adjusted ER:** 0-1 (thực tế 0.02-0.15)
- **Confidence:** 0-1
- **Freshness:** 0.3-1.0
- **Viral Boost:** 1.0-2.0
- **× 100** để scale lên

**Công thức:**
```
Video Score = scaled_views × adjusted_ER × confidence × freshness × viral_boost × 100
```

---

## 🏆 Phân loại KOL theo Điểm

### 🥇 Tier S - Xuất sắc (Score ≥ 40)
**Đặc điểm:**
- Views ổn định cao (10K-100K+)
- ER tốt (≥ 5%)
- Video viral thường xuyên
- Độ tin cậy cao

**Khuyến nghị:**
- ✅ **HỢP TÁC DÀI HẠN**
- Đầu tư ngân sách cao
- Ưu tiên sản phẩm chủ lực
- Xây dựng quan hệ lâu dài

**Ví dụ:**
```
Video 1: 50K views, ER 6%, 10 ngày
→ Score: 4.7 × 0.06 × 1.0 × 1.0 × 1.5 × 100 = 42.3

Video 2: 30K views, ER 7%, 5 ngày
→ Score: 4.5 × 0.07 × 1.0 × 1.0 × 1.4 × 100 = 44.1

KOL Score: ~43
```

---

### 🥈 Tier A - Tốt (Score 25-40)
**Đặc điểm:**
- Views ổn định (5K-20K)
- ER khá (4-6%)
- Có video viral thỉnh thoảng
- Đáng tin cậy

**Khuyến nghị:**
- ✅ **HỢP TÁC TRUNG HẠN**
- Ngân sách vừa phải
- Test với nhiều sản phẩm
- Theo dõi hiệu suất

**Ví dụ:**
```
Video 1: 10K views, ER 5%, 15 ngày
→ Score: 4.0 × 0.05 × 1.0 × 0.9 × 1.3 × 100 = 23.4

Video 2: 15K views, ER 6%, 8 ngày
→ Score: 4.2 × 0.06 × 1.0 × 1.0 × 1.35 × 100 = 34.0

KOL Score: ~30
```

---

### 🥉 Tier B - Khá (Score 15-25)
**Đặc điểm:**
- Views dao động (2K-10K)
- ER trung bình (3-5%)
- Hiệu suất không ổn định
- Cần quan sát thêm

**Khuyến nghị:**
- ⚠️ **HỢP TÁC THỬ NGHIỆM**
- Ngân sách thấp
- Sản phẩm phụ hoặc test
- Đánh giá sau 2-3 video

**Ví dụ:**
```
Video 1: 5K views, ER 4%, 20 ngày
→ Score: 3.7 × 0.04 × 1.0 × 0.9 × 1.2 × 100 = 16.0

Video 2: 3K views, ER 5%, 30 ngày
→ Score: 3.5 × 0.05 × 0.6 × 0.9 × 1.15 × 100 = 10.9

KOL Score: ~18
```

---

### ❌ Tier C - Yếu (Score < 15)
**Đặc điểm:**
- Views thấp (< 2K)
- ER thấp (< 3%)
- Không có video nổi bật
- Hiệu suất kém

**Khuyến nghị:**
- ❌ **KHÔNG NÊN HỢP TÁC**
- Hoặc chỉ hợp tác barter (trao đổi sản phẩm)
- Không đầu tư tiền
- Tìm KOL khác

**Ví dụ:**
```
Video 1: 1K views, ER 2%, 40 ngày
→ Score: 3.0 × 0.02 × 0.2 × 0.7 × 1.1 × 100 = 0.9

Video 2: 2K views, ER 3%, 50 ngày
→ Score: 3.3 × 0.03 × 0.4 × 0.6 × 1.12 × 100 = 2.7

KOL Score: ~5
```

---

## 🎯 Ngưỡng Khuyến nghị Chi tiết

| Score | Tier | Quyết định | Ngân sách | ROI kỳ vọng |
|-------|------|------------|-----------|-------------|
| **≥ 40** | S | ✅ Hợp tác ngay | Cao (5-10M+) | Rất cao |
| **30-40** | A+ | ✅ Hợp tác | Khá (3-5M) | Cao |
| **25-30** | A | ✅ Hợp tác | Vừa (2-3M) | Tốt |
| **20-25** | B+ | ⚠️ Cân nhắc | Thấp (1-2M) | Trung bình |
| **15-20** | B | ⚠️ Test nhỏ | Rất thấp (500K-1M) | Thấp |
| **10-15** | C+ | ❌ Barter only | 0đ (chỉ sản phẩm) | Rất thấp |
| **< 10** | C | ❌ Không hợp tác | 0đ | Không |

---

## 📈 Các yếu tố Bổ sung cần xem xét

### 1. Trend (Xu hướng)
```
Score tăng dần → ✅ Tốt (KOL đang lên)
Score giảm dần → ⚠️ Cảnh báo (KOL đang xuống)
Score ổn định → 👍 OK
```

### 2. Consistency (Tính ổn định)
```
Tất cả video đều > 20 điểm → ✅ Ổn định
Có video 40, có video 5 → ⚠️ Không ổn định
```

### 3. Niche Match (Phù hợp ngách)
```
KOL làm đúng sản phẩm của bạn → +10 điểm bonus
KOL làm sai ngách → -5 điểm penalty
```

### 4. Audience Quality (Chất lượng khán giả)
```
Khán giả đúng target → +5 điểm
Khán giả không phù hợp → -5 điểm
```

---

## 💡 Ví dụ Thực tế

### Case 1: KOL Score = 35 (Tier A)

**Phân tích:**
- 3 videos: 25K, 15K, 10K views
- ER: 5-7%
- Tuổi video: 5-20 ngày
- Viral boost: 1.3-1.5x

**Quyết định:**
✅ **HỢP TÁC** với ngân sách 3-4M
- Kỳ vọng: 30-50K views/video
- ROI: 1:3 đến 1:5
- Thời gian: 3-6 tháng

---

### Case 2: KOL Score = 18 (Tier B)

**Phân tích:**
- 2 videos: 5K, 3K views
- ER: 3-4%
- Tuổi video: 20-40 ngày
- Viral boost: 1.1-1.2x

**Quyết định:**
⚠️ **TEST NHỎ** với ngân sách 500K-1M
- Kỳ vọng: 3-8K views/video
- ROI: 1:1 đến 1:2
- Đánh giá lại sau 2 video

---

### Case 3: KOL Score = 8 (Tier C)

**Phân tích:**
- 2 videos: 1K, 800 views
- ER: 2%
- Tuổi video: 50+ ngày
- Viral boost: 1.0x

**Quyết định:**
❌ **KHÔNG HỢP TÁC**
- Hoặc chỉ barter (tặng sản phẩm)
- Không đầu tư tiền
- Tìm KOL khác tốt hơn

---

## 🎯 Kết luận & Khuyến nghị

### Ngưỡng Tối thiểu:

```
Score ≥ 25: HỢP TÁC TỰ TIN
Score 15-25: CÂN NHẮC / TEST
Score < 15: KHÔNG NÊN
```

### Ngưỡng Lý tưởng:

```
Score ≥ 30: ĐÁNG ĐẦU TƯ
Score ≥ 40: TOP PRIORITY
```

### Công thức Quyết định:

```python
if kol_score >= 40:
    decision = "HỢP TÁC NGAY - Đầu tư cao"
elif kol_score >= 30:
    decision = "HỢP TÁC - Đầu tư vừa"
elif kol_score >= 25:
    decision = "HỢP TÁC - Đầu tư thấp"
elif kol_score >= 20:
    decision = "CÂN NHẮC - Test nhỏ"
elif kol_score >= 15:
    decision = "TEST - Ngân sách tối thiểu"
else:
    decision = "KHÔNG HỢP TÁC hoặc Barter only"
```

---

## 📊 Thống kê Tham khảo

Dựa trên dữ liệu thực tế:

- **Top 10% KOL:** Score ≥ 35
- **Top 25% KOL:** Score ≥ 25
- **Top 50% KOL:** Score ≥ 18
- **Bottom 50% KOL:** Score < 18

**Khuyến nghị:**
- Tập trung vào **Top 25%** (Score ≥ 25)
- Đầu tư mạnh vào **Top 10%** (Score ≥ 35)
- Tránh **Bottom 50%** (Score < 18)

---

## 🚀 Action Items

1. **Lọc KOL:** Score ≥ 25
2. **Ưu tiên:** Score ≥ 35
3. **Test:** Score 20-25
4. **Loại bỏ:** Score < 15
5. **Review định kỳ:** Mỗi tháng cập nhật score

**Mục tiêu:** Chỉ hợp tác với KOL có ROI tích cực!
