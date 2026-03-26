# 🏆 Công thức Xếp hạng KOL

## 📊 Tổng quan

Xếp hạng KOL dựa trên **hiệu suất video trong 3 tháng gần nhất**, cân bằng:
- Views (lượt xem)
- Engagement Rate (tỷ lệ tương tác)
- Freshness (độ mới)
- Viral potential (khả năng viral)
- Confidence (độ tin cậy)

---

## 🎯 Công thức

### 1. Video Score (điểm từng video)

```
Video Score = scaled_views × adjusted_ER × confidence × freshness × viral_boost × 100
```

#### Các thành phần:

**a) Scaled Views** - Giảm bias từ views lớn
```
scaled_views = log₁₀(views + 1)

Ví dụ:
- 1,000 views → 3.0
- 10,000 views → 4.0
- 100,000 views → 5.0
```

**b) Adjusted ER** - Tránh ER ảo khi views thấp
```
adjusted_ER = (total_engagement + 50) / (views + 50)

total_engagement = likes + comments + shares + saves
```

**c) Confidence** - Độ tin cậy dựa trên views
```
confidence = min(1, views / 5000)

Ví dụ:
- 1,000 views → 0.2 (20%)
- 2,500 views → 0.5 (50%)
- 5,000+ views → 1.0 (100%)
```

**d) Freshness** - Độ mới của video
```
age ≤ 3 ngày:        freshness = 0.8  (cho cơ hội detect viral)
3 < age ≤ 14 ngày:   freshness = 1.0  (peak viral window)
14 < age ≤ 30 ngày:  freshness = 0.9  (đã xác thực)
age > 30 ngày:       freshness = e^(-(age-30)/60)  (giảm chậm)

Ví dụ:
- 2 ngày → 0.8
- 7 ngày → 1.0
- 20 ngày → 0.9
- 60 ngày → 0.55
- 90 ngày → 0.33
```

**e) Viral Boost** - Khả năng viral (có cap)
```
β = max(100, follower × 0.05)
viral_boost = min(2.0, 1 + 0.4 × log₁₀(views / (follower + β) + 1))

Ví dụ:
- KOL 1K follower, 10K views → boost = 1.49
- KOL 1K follower, 100K views → boost = 1.78
- KOL 100K follower, 1M views → boost = 1.40
```

---

### 2. KOL Score (điểm cuối cùng)

```
KOL Score = Σ(video_score × weight) / Σ(weight)

weight = log₁₀(views + 1) × confidence
```

**Ý nghĩa:**
- Video có nhiều views + confidence cao → trọng số lớn
- Trung bình có trọng số → phản ánh hiệu suất tổng thể

---

## 📈 Ví dụ thực tế

### KOL: lamtunga1101

**Video 1:**
- Views: 1,584 | ER: 8.7% | Age: 81 ngày
- Score: 16.36

**Video 2:**
- Views: 3,529 | ER: 5.8% | Age: 79 ngày  
- Score: 11.88

**KOL Score:**
```
weight₁ = 3.20 × 0.317 = 1.014
weight₂ = 3.55 × 0.706 = 2.506

KOL Score = (16.36 × 1.014 + 11.88 × 2.506) / (1.014 + 2.506)
          = 46.36 / 3.52
          = 13.17 ≈ 14.00
```

---

## 🔍 Filter & Rules

### Lọc video
- ✅ Chỉ lấy video trong **90 ngày gần nhất**
- ❌ Bỏ video có `views < 50`
- ❌ Bỏ video có `error != ""`

### Xếp hạng
- Sắp xếp theo `KOL Score` giảm dần
- #1 = KOL có score cao nhất

---

## ✅ Lợi ích

1. **Công bằng**
   - KOL nhỏ có ER cao vẫn có cơ hội top
   - Không bị "auto win" bởi views lớn

2. **Ưu tiên video mới**
   - Video 3-14 ngày được trust tối đa (peak viral window)
   - Video cũ giảm ảnh hưởng chậm

3. **Cân bằng**
   - Views + ER + Freshness + Viral
   - Không bias KOL lớn hay nhỏ

4. **Chống gaming**
   - Confidence cao (5K views) giảm ảnh hưởng video ít views
   - Adjusted ER tránh ER ảo
   - Viral boost capped 2.0 tránh extreme cases

---

## 🚀 Implementation

**Backend:** `backend-data/kol_management/video_scoring.py`

**API:** `POST /api/kol/ranking`

```python
from kol_management.video_scoring import rank_kols_by_score

ranked_kols = rank_kols_by_score(kols, method='weighted')
```

---

## 📝 Constants

```python
DAYS_THRESHOLD = 90           # Lọc video trong 3 tháng
MIN_VIEWS_THRESHOLD = 50      # Lọc video quá ít views
CONFIDENCE_THRESHOLD = 5000   # Views cần để đạt confidence = 1
FRESHNESS_DECAY = 60          # Hệ số decay sau 30 ngày
VIRAL_ALPHA = 0.4             # Độ mạnh viral boost
VIRAL_BETA_MIN = 100          # Beta tối thiểu
VIRAL_BETA_RATIO = 0.05       # Beta = 5% follower
VIRAL_BOOST_CAP = 2.0         # Cap viral boost tối đa
K_ADJUSTMENT = 50             # Hệ số điều chỉnh ER
```
