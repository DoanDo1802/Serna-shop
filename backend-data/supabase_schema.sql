-- ============================================
-- SUPABASE DATABASE SCHEMA
-- ============================================

-- 1. Bảng Products (Sản phẩm)
-- ============================================
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    specifications TEXT,
    price NUMERIC NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('in_stock', 'out_of_stock')),
    image TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Index cho tìm kiếm
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Policy: Cho phép đọc công khai
CREATE POLICY "Allow public read access on products"
ON products FOR SELECT
USING (true);

-- Policy: Cho phép insert/update/delete với service role
CREATE POLICY "Allow authenticated insert on products"
ON products FOR INSERT
WITH CHECK (true);

CREATE POLICY "Allow authenticated update on products"
ON products FOR UPDATE
USING (true);

CREATE POLICY "Allow authenticated delete on products"
ON products FOR DELETE
USING (true);


-- 2. Bảng Kalodata Creators (KOL)
-- ============================================
CREATE TABLE IF NOT EXISTS kalodata_creators (
    id SERIAL PRIMARY KEY,
    period TEXT NOT NULL,
    name TEXT NOT NULL,
    followers INTEGER NOT NULL DEFAULT 0,
    revenue_livestream NUMERIC NOT NULL DEFAULT 0,
    revenue_video NUMERIC NOT NULL DEFAULT 0,
    kalodata_url TEXT,
    tiktok_url TEXT,
    age_range TEXT,
    gender TEXT,
    engagement_rate NUMERIC,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Index cho tìm kiếm và filter
CREATE INDEX IF NOT EXISTS idx_creators_name ON kalodata_creators(name);
CREATE INDEX IF NOT EXISTS idx_creators_followers ON kalodata_creators(followers DESC);
CREATE INDEX IF NOT EXISTS idx_creators_revenue_livestream ON kalodata_creators(revenue_livestream DESC);
CREATE INDEX IF NOT EXISTS idx_creators_revenue_video ON kalodata_creators(revenue_video DESC);
CREATE INDEX IF NOT EXISTS idx_creators_engagement_rate ON kalodata_creators(engagement_rate DESC);
CREATE INDEX IF NOT EXISTS idx_creators_created_at ON kalodata_creators(created_at DESC);

-- Unique constraint để tránh duplicate
CREATE UNIQUE INDEX IF NOT EXISTS idx_creators_unique 
ON kalodata_creators(name, period, kalodata_url);

-- Enable Row Level Security (RLS)
ALTER TABLE kalodata_creators ENABLE ROW LEVEL SECURITY;

-- Policy: Cho phép đọc công khai
CREATE POLICY "Allow public read access on kalodata_creators"
ON kalodata_creators FOR SELECT
USING (true);

-- Policy: Cho phép insert/update/delete với service role
CREATE POLICY "Allow authenticated insert on kalodata_creators"
ON kalodata_creators FOR INSERT
WITH CHECK (true);

CREATE POLICY "Allow authenticated update on kalodata_creators"
ON kalodata_creators FOR UPDATE
USING (true);

CREATE POLICY "Allow authenticated delete on kalodata_creators"
ON kalodata_creators FOR DELETE
USING (true);


-- 3. Bảng Metadata (Thông tin cập nhật)
-- ============================================
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value JSONB,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE metadata ENABLE ROW LEVEL SECURITY;

-- Policy: Cho phép đọc công khai
CREATE POLICY "Allow public read access on metadata"
ON metadata FOR SELECT
USING (true);

-- Policy: Cho phép insert/update với service role
CREATE POLICY "Allow authenticated upsert on metadata"
ON metadata FOR INSERT
WITH CHECK (true);

CREATE POLICY "Allow authenticated update on metadata"
ON metadata FOR UPDATE
USING (true);


-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Function: Tự động cập nhật updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger cho products
DROP TRIGGER IF EXISTS update_products_updated_at ON products;
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger cho kalodata_creators
DROP TRIGGER IF EXISTS update_creators_updated_at ON kalodata_creators;
CREATE TRIGGER update_creators_updated_at
    BEFORE UPDATE ON kalodata_creators
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger cho metadata
DROP TRIGGER IF EXISTS update_metadata_updated_at ON metadata;
CREATE TRIGGER update_metadata_updated_at
    BEFORE UPDATE ON metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================
-- INITIAL DATA
-- ============================================

-- Insert metadata keys
INSERT INTO metadata (key, value) VALUES
    ('products_last_sync', '{"count": 0, "timestamp": null}'::jsonb),
    ('creators_last_sync', '{"count": 0, "timestamp": null}'::jsonb)
ON CONFLICT (key) DO NOTHING;
