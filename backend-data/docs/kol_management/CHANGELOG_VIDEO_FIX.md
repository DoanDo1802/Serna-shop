# Changelog: Video Count & Ranking Fix

## Version: 2024-03-27

### 🐛 Bug Fixes

#### 1. Video Count Display Issue
**Problem:**
- KOL có video nhưng hiển thị "0 video"
- Chỉ đếm video trong 90 ngày, bỏ qua video cũ

**Solution:**
- Thêm field `total_videos` để lưu tổng số video (bao gồm cả video cũ)
- Hiển thị cả 2 số: `total_scored_videos` (90d) và `total_videos` (tổng)
- UI: "Videos (90d/Tổng)" với 2 badge khi có video cũ

#### 2. Ranking Issue
**Problem:**
- KOL có video cũ (>90 ngày) bị xếp xuống dưới cùng
- Ranking chỉ dựa vào `kol_score`, không xét `total_videos`

**Solution:**
- Ranking mới: sort theo `(kol_score DESC, total_videos DESC)`
- KOL có cùng score → xếp theo số lượng video
- KOL có video cũ vẫn được xếp hạng đúng

#### 3. Logging Improvement
**Problem:**
- Log không rõ ràng về số video được tính điểm

**Solution:**
- Log format mới: `"X/Y videos được tính điểm"`
- Hiển thị rõ video nào trong 90 ngày, video nào cũ hơn

### 📝 Changes

#### Backend Files

**1. `video_scoring.py`**
```python
# Added
- total_videos = len([v for v in videos if not v.get('error') and v.get('views', 0) >= MIN_VIEWS_THRESHOLD])
- kol['total_videos'] = total_videos

# Modified
- score_kol_videos(): Thêm logging cho total_videos
- rank_kols_by_score(): Sort theo (kol_score, total_videos)
```

**2. `supabase_kol_store.py`**
```python
# Added
- 'total_videos': kol_data.get('total_videos', 0)  # Save to DB
- 'total_videos': row.get('total_videos', 0)  # Read from DB
```

**3. `supabase_kol_schema.sql`**
```sql
-- Added
ALTER TABLE kols ADD COLUMN total_videos INTEGER DEFAULT 0;
COMMENT ON COLUMN kols.total_videos IS 'Tổng số video (bao gồm cả video cũ hơn 90 ngày)';
```

#### Frontend Files

**1. `lib/api.ts`**
```typescript
// Added to interface KOL
total_videos?: number // Tổng số video (bao gồm cả video cũ)
```

**2. `app/kol-management/page.tsx`**
```tsx
// Changed header
<TableHead>Videos (90d/Tổng)</TableHead>

// Added logic
const scoredVideos = kol.total_scored_videos || 0
const totalVideos = kol.total_videos || kol.videos?.length || 0
const hasOldVideos = totalVideos > scoredVideos

// Conditional rendering
{hasOldVideos ? (
  <div>
    <Badge>{scoredVideos}</Badge>
    <Badge variant="outline">/{totalVideos} tổng</Badge>
  </div>
) : (
  <Badge variant="outline">{totalVideos}</Badge>
)}
```

### 🔧 Migration Required

**File:** `migration_add_total_videos.sql`

```sql
-- 1. Add column
ALTER TABLE kols ADD COLUMN IF NOT EXISTS total_videos INTEGER DEFAULT 0;

-- 2. Populate data
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

### 📊 Testing

#### Test Cases

**Case 1: KOL có tất cả video mới (<90 ngày)**
- Input: 5 videos, tất cả < 90 ngày
- Expected: 
  - `total_scored_videos = 5`
  - `total_videos = 5`
  - UI: Badge "5" (outline)

**Case 2: KOL có video cũ và mới**
- Input: 8 videos (3 mới, 5 cũ)
- Expected:
  - `total_scored_videos = 3`
  - `total_videos = 8`
  - UI: Badge "3" + Badge "/8 tổng"

**Case 3: KOL chỉ có video cũ (>90 ngày)**
- Input: 3 videos, tất cả > 90 ngày
- Expected:
  - `total_scored_videos = 0`
  - `total_videos = 3`
  - `kol_score = 0`
  - UI: Badge "0" + Badge "/3 tổng"
  - Ranking: Xếp cuối nhưng vẫn có rank

### 🚀 Deployment Steps

1. **Database Migration**
   ```bash
   # Run in Supabase SQL Editor
   backend-data/kol_management/migration_add_total_videos.sql
   ```

2. **Backend Restart**
   ```bash
   cd backend-data
   # Stop current process
   python app.py
   ```

3. **Frontend Rebuild**
   ```bash
   cd frontend-base
   npm run dev
   ```

4. **Data Refresh**
   - Open KOL Management page
   - Click "Cập nhật từ TikTok"
   - Verify display

### ✅ Verification

**Database Check:**
```sql
SELECT 
    tiktok_account,
    rank,
    kol_score,
    total_scored_videos,
    total_videos,
    (total_videos - total_scored_videos) as old_videos
FROM kols
ORDER BY rank ASC NULLS LAST
LIMIT 10;
```

**Expected Results:**
- All KOLs have `total_videos >= total_scored_videos`
- KOLs with old videos show correct counts
- Ranking is correct (score DESC, then total_videos DESC)

### 📚 Documentation

**New Files:**
- `VIDEO_COUNT_FIX.md` - User guide
- `CHANGELOG_VIDEO_FIX.md` - This file
- `migration_add_total_videos.sql` - Database migration

**Updated Files:**
- `video_scoring.py` - Scoring logic
- `supabase_kol_store.py` - Database operations
- `supabase_kol_schema.sql` - Schema definition
- `lib/api.ts` - Type definitions
- `app/kol-management/page.tsx` - UI display

### 🔍 Impact Analysis

**Breaking Changes:** None
- Backward compatible
- Old data still works (total_videos defaults to 0)
- Migration updates existing records

**Performance Impact:** Minimal
- One additional column in database
- No additional queries
- Sorting slightly more complex but negligible

**User Experience:** Improved
- More accurate video counts
- Better ranking fairness
- Clearer UI with 2-number display

### 🐛 Known Issues

None at this time.

### 📝 Notes

- Video cũ hơn 90 ngày vẫn được lưu trong database
- Không tính điểm nhưng vẫn hiển thị số lượng
- Giúp theo dõi lịch sử hoạt động KOL
- Ranking công bằng hơn cho KOL có video cũ

### 👥 Contributors

- Fixed by: Kiro AI Assistant
- Date: 2024-03-27
- Requested by: User (Vietnamese)
