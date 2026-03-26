# Backend KOL Data Management System

Hệ thống backend hoàn chỉnh để quản lý dữ liệu KOL từ Kalodata và TikTok.

## Tính năng

### 1. Kalodata Integration
- Export dữ liệu KOL với bộ lọc tùy chỉnh (độ tuổi, doanh thu, thời gian)
- Phân tích chi tiết follower (giới tính, độ tuổi, tỷ lệ tương tác)
- Tự động loại bỏ dữ liệu trùng lặp
- Lưu trữ dữ liệu trên Supabase (cloud database)
- Upload lên Google Sheets

### 2. TikTok Integration
- Lấy danh sách video từ profile TikTok
- Lấy thông tin user (User ID, SecUid)
- Gửi tin nhắn tự động (DM)
- Gửi tin nhắn hàng loạt

### 3. Product Management
- CRUD operations cho sản phẩm
- Lưu trữ trên Supabase
- Hỗ trợ upload ảnh sản phẩm

### 4. AI Agent Mode
- Gợi ý filter KOL dựa trên sản phẩm
- Phân tích sản phẩm và đề xuất target audience

## Cài đặt

### 1. Cài đặt dependencies

```bash
cd backend-data
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
playwright install chromium
```

### 2. Cấu hình

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

#### Cách 1: Tự động lấy Cookie (Khuyến nghị ⭐)

```bash
# Tự động lấy và update cookie vào .env
python3 update_cookies.py

# Hoặc chỉ lấy Kalodata
python3 update_cookies.py --kalodata

# Hoặc chỉ lấy TikTok
python3 update_cookies.py --tiktok
```

Xem hướng dẫn chi tiết: [COOKIE_GUIDE.md](./COOKIE_GUIDE.md)

#### Cách 2: Thủ công (Cách cũ)

Chỉnh sửa file `.env` với thông tin của bạn:
- `KALODATA_COOKIE`: Cookie từ trình duyệt sau khi đăng nhập Kalodata
- `TIKTOK_COOKIE`: Cookie từ trình duyệt sau khi đăng nhập TikTok
- `GOOGLE_SHEET_URL`: URL của Google Sheet để lưu dữ liệu
- `SUPABASE_URL`: URL của Supabase project
- `SUPABASE_KEY`: Service role key của Supabase

### 3. Setup Supabase

Xem hướng dẫn chi tiết trong [SUPABASE_SETUP.md](./SUPABASE_SETUP.md)

1. Tạo project trên Supabase
2. Chạy SQL schema từ file `supabase_schema.sql`
3. Copy URL và Service Role Key vào `.env`

### 4. Cấu hình Google Sheets API

1. Tạo Service Account trên Google Cloud Console
2. Download file JSON credentials
3. Lưu vào `kalodata/google_credentials.json`
4. Chia sẻ Google Sheet với email service account (quyền Editor)

## Chạy Backend

```bash
source venv/bin/activate
python app.py
```

Server sẽ chạy tại: `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /health
```

### Kalodata APIs

#### Lấy dữ liệu KOL đã lưu
```
GET /api/kalodata/data
```

#### Export dữ liệu KOL mới
```
POST /api/kalodata/export
Content-Type: application/json

{
  "start_date": "2026-02-14",
  "end_date": "2026-03-14",
  "revenue_min": 50000000,
  "revenue_max": 100000000,
  "age_range": "25-34",
  "enrich": true,
  "deduplicate": true
}
```

#### Xóa KOL
```
POST /api/kalodata/delete
Content-Type: application/json

{
  "names": ["Tên KOL 1", "Tên KOL 2"]
}
```

#### Upload lên Google Sheets
```
POST /api/kalodata/upload
Content-Type: application/json

{
  "excel_path": "kalodata/exports/export_kalodata_20260314_120000.xlsx",
  "google_sheet_url": "https://docs.google.com/spreadsheets/d/...",
  "sheet_name": "Sheet1"
}
```

### Product APIs

#### Lấy tất cả sản phẩm
```
GET /api/products
```

#### Lấy một sản phẩm
```
GET /api/products/{product_id}
```

#### Thêm sản phẩm
```
POST /api/products
Content-Type: application/json

{
  "name": "Tên sản phẩm",
  "description": "Mô tả",
  "specifications": "Thông số kỹ thuật",
  "price": 150000,
  "status": "in_stock",
  "image": "base64 hoặc URL"
}
```

#### Cập nhật sản phẩm
```
PUT /api/products/{product_id}
Content-Type: application/json

{
  "name": "Tên mới",
  "price": 200000
}
```

#### Xóa sản phẩm
```
DELETE /api/products/{product_id}
```

#### Xóa nhiều sản phẩm
```
POST /api/products/batch-delete
Content-Type: application/json

{
  "ids": ["id1", "id2", "id3"]
}
```

### Agent APIs

#### Gợi ý filter KOL
```
POST /api/agent/suggest
Content-Type: application/json

{
  "description": "Mô tả sản phẩm",
  "price": "150000",
  "image": "base64 encoded image (optional)"
}
```

### TikTok APIs

#### Lấy danh sách video
```
POST /api/tiktok/videos
Content-Type: application/json

{
  "profile_url": "https://www.tiktok.com/@username"
}
```

#### Lấy User ID
```
POST /api/tiktok/userid
Content-Type: application/json

{
  "profile_url": "https://www.tiktok.com/@username"
}
```

#### Gửi tin nhắn đơn
```
POST /api/tiktok/send-dm
Content-Type: application/json

{
  "profile_url": "https://www.tiktok.com/@username",
  "message": "Xin chào, chúng ta có thể hợp tác không?"
}
```

#### Gửi tin nhắn hàng loạt
```
POST /api/tiktok/batch-dm
Content-Type: application/json

{
  "users": [
    {
      "profile_url": "https://www.tiktok.com/@user1",
      "message": "Tin nhắn cho user 1"
    },
    {
      "profile_url": "https://www.tiktok.com/@user2",
      "message": "Tin nhắn cho user 2"
    }
  ]
}
```

## Ví dụ sử dụng với curl

### Lấy video TikTok
```bash
curl -X POST http://localhost:5000/api/tiktok/videos \
  -H "Content-Type: application/json" \
  -d '{"profile_url": "https://www.tiktok.com/@cohocchamda"}'
```

### Gửi tin nhắn TikTok
```bash
curl -X POST http://localhost:5000/api/tiktok/send-dm \
  -H "Content-Type: application/json" \
  -d '{
    "profile_url": "https://www.tiktok.com/@username",
    "message": "Xin chào!"
  }'
```

## Cấu trúc thư mục

```
backend-data/
├── app.py                      # Flask API server
├── requirements.txt            # Python dependencies
├── .env                        # Cấu hình (không commit)
├── .env.example               # Mẫu cấu hình
├── README.md                  # Tài liệu này
├── SUPABASE_SETUP.md          # Hướng dẫn setup Supabase
├── MIGRATION_COMPLETE.md      # Thông tin migration
├── supabase_client.py         # Supabase client helper
├── supabase_schema.sql        # SQL schema cho Supabase
├── kalodata/                  # Module Kalodata
│   ├── data_store.py         # CRUD operations với Supabase
│   ├── exp_playwright_api.py # Export dữ liệu
│   ├── datakoc.py            # Phân tích follower
│   ├── process_all.py        # Xử lý dữ liệu
│   ├── upload_sheets.py      # Upload Google Sheets
│   ├── .cookie               # Cookie Kalodata
│   ├── google_credentials.json # Google API credentials
│   └── exports/              # Thư mục chứa file export
├── products/                  # Module Products
│   └── product_store.py      # CRUD operations với Supabase
├── agent/                     # Module AI Agent
│   ├── agent.py              # Agent logic
│   └── skills.py             # Agent skills
└── tiktok/                   # Module TikTok
    ├── tiktok.py             # Lấy video
    ├── get_userid.py         # Lấy User ID
    ├── dmtiktok.py           # Gửi tin nhắn
    └── .tiktok_cookie        # Cookie TikTok
```

## Lưu ý

1. **Cookie**: 
   - **Tự động**: Dùng `python3 update_cookies.py` để tự động lấy và refresh cookie
   - **Thủ công**: Cookie có thời hạn, cần cập nhật định kỳ khi hết hạn
   - Xem chi tiết: [COOKIE_GUIDE.md](./COOKIE_GUIDE.md)
2. **Rate Limiting**: Tránh gửi quá nhiều request trong thời gian ngắn
3. **Headless Mode**: Có thể bật headless=True trong Playwright để chạy ngầm
4. **Security**: Không commit file `.env`, `.cookie`, `google_credentials.json`

## Troubleshooting

### Lỗi Cookie hết hạn
**Giải pháp tự động (Khuyến nghị):**
```bash
python3 update_cookies.py --force
```

**Giải pháp thủ công:**
- Đăng nhập lại vào Kalodata/TikTok
- Copy cookie mới từ DevTools
- Cập nhật vào file `.env` hoặc `.cookie`

### Lỗi Google Sheets Permission
- Kiểm tra email service account đã được chia sẻ quyền Editor
- Kiểm tra file `google_credentials.json` đúng định dạng

### Playwright không tìm thấy browser
```bash
playwright install chromium
```

## License

MIT
