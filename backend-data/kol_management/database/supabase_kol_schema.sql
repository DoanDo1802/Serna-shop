-- ============================================
-- SUPABASE SCHEMA FOR KOL MANAGEMENT
-- ============================================

-- 1. Bảng KOL (Thông tin KOL cơ bản)
-- ============================================
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
    total_scored_videos INTEGER DEFAULT 0, -- Số video trong 90 ngày được tính điểm
    total_videos INTEGER DEFAULT 0, -- Tổng số video (bao gồm cả video cũ)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Unique constraint: Mỗi KOL chỉ có 1 record cho mỗi sheet
    CONSTRAINT unique_kol_per_sheet UNIQUE (tiktok_account, sheet_url, sheet_name)
);

-- 2. Bảng Videos (Thông tin chi tiết từng video)
-- ============================================
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
    posted_at TIMESTAMPTZ, -- Thời gian đăng video
    days_since_posted INTEGER, -- Số ngày kể từ khi đăng (12d, 5d, etc.)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Unique constraint: Mỗi video chỉ có 1 record cho mỗi KOL
    CONSTRAINT unique_video_per_kol UNIQUE (kol_id, video_id)
);

-- 3. Bảng Total Stats (Tổng hợp stats của KOL)
-- ============================================
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
    
    -- Mỗi KOL chỉ có 1 record total stats
    CONSTRAINT unique_stats_per_kol UNIQUE (kol_id)
);

-- ============================================
-- INDEXES
-- ============================================

-- KOLs indexes
CREATE INDEX IF NOT EXISTS idx_kols_tiktok_account ON kols(tiktok_account);
CREATE INDEX IF NOT EXISTS idx_kols_sheet ON kols(sheet_url, sheet_name);
CREATE INDEX IF NOT EXISTS idx_kols_rank ON kols(rank);
CREATE INDEX IF NOT EXISTS idx_kols_score ON kols(kol_score DESC);
CREATE INDEX IF NOT EXISTS idx_kols_updated_at ON kols(updated_at DESC);

-- Videos indexes
CREATE INDEX IF NOT EXISTS idx_videos_kol_id ON kol_videos(kol_id);
CREATE INDEX IF NOT EXISTS idx_videos_video_id ON kol_videos(video_id);
CREATE INDEX IF NOT EXISTS idx_videos_posted_at ON kol_videos(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_videos_days_since ON kol_videos(days_since_posted);

-- Stats indexes
CREATE INDEX IF NOT EXISTS idx_stats_kol_id ON kol_total_stats(kol_id);

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

ALTER TABLE kols ENABLE ROW LEVEL SECURITY;
ALTER TABLE kol_videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE kol_total_stats ENABLE ROW LEVEL SECURITY;

-- Policies: Cho phép đọc công khai
CREATE POLICY "Allow public read access on kols"
ON kols FOR SELECT USING (true);

CREATE POLICY "Allow public read access on kol_videos"
ON kol_videos FOR SELECT USING (true);

CREATE POLICY "Allow public read access on kol_total_stats"
ON kol_total_stats FOR SELECT USING (true);

-- Policies: Cho phép insert/update/delete với service role
CREATE POLICY "Allow authenticated operations on kols"
ON kols FOR ALL USING (true);

CREATE POLICY "Allow authenticated operations on kol_videos"
ON kol_videos FOR ALL USING (true);

CREATE POLICY "Allow authenticated operations on kol_total_stats"
ON kol_total_stats FOR ALL USING (true);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Function: Tự động cập nhật updated_at
CREATE OR REPLACE FUNCTION update_kol_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
DROP TRIGGER IF EXISTS update_kols_updated_at ON kols;
CREATE TRIGGER update_kols_updated_at
    BEFORE UPDATE ON kols
    FOR EACH ROW
    EXECUTE FUNCTION update_kol_updated_at();

DROP TRIGGER IF EXISTS update_videos_updated_at ON kol_videos;
CREATE TRIGGER update_videos_updated_at
    BEFORE UPDATE ON kol_videos
    FOR EACH ROW
    EXECUTE FUNCTION update_kol_updated_at();

DROP TRIGGER IF EXISTS update_stats_updated_at ON kol_total_stats;
CREATE TRIGGER update_stats_updated_at
    BEFORE UPDATE ON kol_total_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_kol_updated_at();

-- Function: Tính toán days_since_posted từ posted_at
CREATE OR REPLACE FUNCTION calculate_days_since_posted()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.posted_at IS NOT NULL THEN
        NEW.days_since_posted = EXTRACT(DAY FROM (NOW() - NEW.posted_at))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger: Auto-calculate days_since_posted
DROP TRIGGER IF EXISTS calc_days_since_posted ON kol_videos;
CREATE TRIGGER calc_days_since_posted
    BEFORE INSERT OR UPDATE ON kol_videos
    FOR EACH ROW
    EXECUTE FUNCTION calculate_days_since_posted();

-- ============================================
-- VIEWS (Optional - để query dễ hơn)
-- ============================================

-- View: KOL với đầy đủ thông tin (bao gồm stats và videos)
CREATE OR REPLACE VIEW kol_full_details AS
SELECT 
    k.id,
    k.tiktok_account,
    k.tiktok_link,
    k.product,
    k.sheet_url,
    k.sheet_name,
    k.post_count,
    k.rank,
    k.kol_score,
    k.total_scored_videos,
    k.created_at,
    k.updated_at,
    -- Total stats
    s.total_likes,
    s.total_comments,
    s.total_shares,
    s.total_views,
    s.total_engagement,
    s.avg_engagement_rate,
    -- Video count
    COUNT(v.id) as video_count
FROM kols k
LEFT JOIN kol_total_stats s ON k.id = s.kol_id
LEFT JOIN kol_videos v ON k.id = v.kol_id
GROUP BY 
    k.id, k.tiktok_account, k.tiktok_link, k.product, 
    k.sheet_url, k.sheet_name, k.post_count, k.rank, 
    k.kol_score, k.total_scored_videos, k.created_at, k.updated_at,
    s.total_likes, s.total_comments, s.total_shares, 
    s.total_views, s.total_engagement, s.avg_engagement_rate;

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function: Lấy ranking KOL theo sheet
CREATE OR REPLACE FUNCTION get_kol_ranking(
    p_sheet_url TEXT,
    p_sheet_name TEXT
)
RETURNS TABLE (
    rank INTEGER,
    tiktok_account TEXT,
    tiktok_link TEXT,
    product TEXT,
    kol_score NUMERIC,
    total_scored_videos INTEGER,
    total_views INTEGER,
    total_likes INTEGER,
    total_engagement INTEGER,
    avg_engagement_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        k.rank,
        k.tiktok_account,
        k.tiktok_link,
        k.product,
        k.kol_score,
        k.total_scored_videos,
        s.total_views,
        s.total_likes,
        s.total_engagement,
        s.avg_engagement_rate
    FROM kols k
    LEFT JOIN kol_total_stats s ON k.id = s.kol_id
    WHERE k.sheet_url = p_sheet_url 
      AND k.sheet_name = p_sheet_name
    ORDER BY k.rank ASC NULLS LAST;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON TABLE kols IS 'Bảng lưu thông tin KOL từ Google Sheets';
COMMENT ON TABLE kol_videos IS 'Bảng lưu thông tin chi tiết từng video của KOL';
COMMENT ON TABLE kol_total_stats IS 'Bảng lưu tổng hợp stats của KOL';
COMMENT ON COLUMN kol_videos.days_since_posted IS 'Số ngày kể từ khi đăng video (tự động tính)';
COMMENT ON COLUMN kol_videos.posted_at IS 'Thời gian đăng video (lấy từ TikTok API)';
