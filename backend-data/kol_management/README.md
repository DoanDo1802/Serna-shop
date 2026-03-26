# KOL Management System

Hệ thống quản lý và xếp hạng KOL dựa trên engagement từ TikTok.

## 📋 Tính năng

- ✅ Đọc danh sách KOL từ Google Sheets
- ✅ Lấy stats video TikTok qua n8n webhook (views, likes, comments, shares, saves)
- ✅ Tính engagement rate tự động theo công thức chuẩn TikTok
- ✅ Xếp hạng KOL theo engagement
- ✅ API endpoints cho frontend
- ✅ Giao diện quản lý và ranking

## 📐 Công thức Engagement Rate & Xếp hạng

### Engagement Rate

```
ER = (Like + Comment + Share + Save) / View × 100%
```

**Ví dụ:** 10,000 views, 600 engagement → ER = 6%

### Xếp hạng KOL

Hệ thống xếp hạng phức tạp dựa trên **Video Score** (3 tháng gần nhất).

📖 **Xem chi tiết:** [RANKING_FORMULA.md](./RANKING_FORMULA.md)

**Công thức:**
```
Video Score = Scaled Views × Adjusted ER × Confidence × Freshness × Viral Boost
KOL Score = Weighted Average(Video Scores)
```

**Lợi ích:**
- ✅ Ưu tiên video mới (freshness)
- ✅ KOL nhỏ có ER cao vẫn có cơ hội (viral boost)
- ✅ Cân bằng reach và quality
- ✅ Chống gaming system

## 🚀 Quick Start

### 1. Cài đặt Dependencies

```bash
pip install requests gspread
```

### 2. Setup Google Service Account

1. Tạo Service Account trên Google Cloud Console
2. Download credentials JSON
3. Lưu vào `backend-data/kalodata/google_credentials.json`
4. Chia sẻ Google Sheet với email service account (quyền Editor)

### 3. Setup n8n Workflow

Import workflow vào n8n:
- File: `n8n_tiktok_stats_workflow.json`
- Activate workflow trong n8n UI
- Webhook URL: `https://your-n8n-domain.com/webhook/tiktok-stats`

Chi tiết: [N8N_SETUP_GUIDE.md](./N8N_SETUP_GUIDE.md)

### 4. Cấu hình Environment Variables

```bash
# Thêm vào .env
KOL_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
N8N_WEBHOOK_URL=https://your-n8n-domain.com/webhook/tiktok-stats
```

### 5. Test

```bash
# Test n8n webhook
python3 kol_management/test_n8n_webhook.py

# Test full flow (Google Sheets → n8n → Ranking)
python3 kol_management/test_full_flow.py
```

## 📁 Cấu trúc Files

```
kol_management/
├── README.md                          # File này
├── N8N_SETUP_GUIDE.md                # Hướng dẫn setup n8n chi tiết
├── n8n_tiktok_stats_workflow.json    # n8n workflow definition
│
├── sheets_reader.py                   # Đọc dữ liệu từ Google Sheets
├── tiktok_stats.py                    # Lấy stats từ TikTok (qua n8n)
├── kol_processor.py                   # Xử lý và enrich dữ liệu KOL
│
├── test_n8n_webhook.py                # Test n8n webhook
├── test_full_flow.py                  # Test toàn bộ flow
└── test_kol.py                        # Test đọc sheets (không lấy stats)
```

## 🔧 API Endpoints

### 1. Đồng bộ dữ liệu KOL (không lấy stats)

```bash
POST /api/kol/sync
Content-Type: application/json

{
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/...",
  "sheet_name": "KOL_management",
  "fetch_stats": false
}
```

### 2. Lấy bảng xếp hạng (có lấy stats)

```bash
POST /api/kol/ranking
Content-Type: application/json

{
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/...",
  "sheet_name": "KOL_management"
}
```

Response:
```json
{
  "success": true,
  "ranking": [
    {
      "rank": 1,
      "tiktok_account": "@username",
      "product": "Sản phẩm ABC",
      "post_count": 2,
      "total_stats": {
        "views": 200000,
        "likes": 10000,
        "comments": 500,
        "shares": 200,
        "total_engagement": 10700,
        "avg_engagement_rate": 5.35
      }
    }
  ],
  "total": 10
}
```

## 📊 Google Sheets Format

Sheet name: `KOL_management`

| Cột | Mô tả | Ví dụ |
|-----|-------|-------|
| TIKTOK ACCOUNT | Username TikTok | @username |
| LINK TIKTOK | Link profile | https://www.tiktok.com/@username |
| SẢN PHẨM | Tên sản phẩm | Máy sấy tóc ABC |
| LINK BÀI ĐĂNG | Link videos (nhiều link, mỗi link một dòng hoặc phân cách bằng dấu phẩy) | https://www.tiktok.com/@username/video/123 |

## 🔄 Workflow

```
1. Frontend gọi API /api/kol/ranking
   ↓
2. Backend đọc Google Sheets
   ↓
3. Lấy danh sách KOL + video links
   ↓
4. Gọi n8n webhook cho từng video
   ↓
5. n8n fetch HTML từ TikTok
   ↓
6. n8n parse __UNIVERSAL_DATA_FOR_REHYDRATION__
   ↓
7. n8n trả về stats (views, likes, comments, shares, saves)
   ↓
8. Backend tính engagement rate
   ↓
9. Xếp hạng KOL theo total engagement
   ↓
10. Trả về frontend
```

## 🐛 Troubleshooting

### Lỗi: "n8n webhook error: Connection refused"

**Giải pháp**: Kiểm tra n8n đang chạy và URL đúng trong `.env`

### Lỗi: "Failed to sync KOL data"

**Giải pháp**: 
1. Chia sẻ Sheet với service account email
2. Kiểm tra credentials file tồn tại
3. Kiểm tra sheet name đúng

### Stats trả về 0

**Giải pháp**:
1. Kiểm tra n8n workflow đã activate chưa
2. Test trực tiếp n8n webhook bằng curl
3. Xem execution history trong n8n UI

## 📈 Performance

- **Tốc độ**: ~2-3 giây/video (qua n8n)
- **Khuyến nghị**: Giới hạn 10-20 videos/phút để tránh rate limit

## 🔐 Security

- ⚠️ Không commit credentials vào git
- ⚠️ Sử dụng environment variables
- ⚠️ Bảo mật n8n webhook endpoint

## 📝 Frontend Usage

```typescript
// Lấy bảng xếp hạng
const result = await getKOLRanking(sheetUrl, 'KOL_management');

if (result.success) {
  setRanking(result.ranking);
}
```

## 👥 Tech Stack

- **Backend**: Python + Flask
- **Frontend**: Next.js + TypeScript  
- **Automation**: n8n
- **Data Source**: Google Sheets
- **Stats Source**: TikTok (via n8n)
