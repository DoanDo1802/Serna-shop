# Hướng dẫn sử dụng Hệ thống Quản lý KOL

## Tổng quan

Hệ thống quản lý KOL giúp bạn:
- Đồng bộ dữ liệu KOL từ Google Sheets
- Lấy thống kê video TikTok tự động qua n8n
- Theo dõi trạng thái đăng bài của KOL
- Xếp hạng KOL theo mức độ tương tác

## Công thức tính Engagement Rate

Hệ thống sử dụng công thức chuẩn cho TikTok/Reels:

### 1. Engagement Rate cho từng video

```
ER = (Like + Comment + Share + Save) / View × 100%
```

**Ví dụ:**
- 10,000 views
- 500 likes, 50 comments, 30 shares, 20 saves
- ER = (500 + 50 + 30 + 20) / 10,000 × 100 = 6%

### 2. Tổng Engagement của KOL

**Tổng Engagement** = Tổng số tương tác của tất cả video của KOL

```
Tổng Engagement = Σ(Likes + Comments + Shares + Saves) của tất cả video
```

**Ví dụ KOL có 3 video:**
- Video 1: 500 + 50 + 30 + 20 = 600 engagement
- Video 2: 250 + 25 + 15 + 10 = 300 engagement  
- Video 3: 400 + 40 + 24 + 16 = 480 engagement
- **Tổng Engagement = 600 + 300 + 480 = 1,380**

### 3. Avg Engagement Rate của KOL

```
Avg ER = Tổng Engagement / Tổng Views × 100%
```

**Ví dụ:**
- Tổng Engagement: 1,380
- Tổng Views: 23,000 (10,000 + 5,000 + 8,000)
- Avg ER = 1,380 / 23,000 × 100 = 6%

### 4. Xếp hạng KOL

**KOL được xếp hạng theo công thức log cân bằng:**

```
Ranking Score = log₁₀(Views) × ER%
```

**Ví dụ:**
- KOL A: log₁₀(100,000) × 5% = 5.0 × 5 = 25.0 score
- KOL B: log₁₀(50,000) × 8% = 4.7 × 8 = 37.6 score
- KOL C: log₁₀(200,000) × 2% = 5.3 × 2 = 10.6 score
- **Xếp hạng: B > A > C**

**Lợi ích của công thức log:**
- ✅ Giảm bias từ views quá lớn (200K views không gấp đôi 100K views)
- ✅ Ưu tiên KOL có ER tốt hơn
- ✅ Cân bằng tốt giữa Reach và Quality
- ✅ KOL có ER cao + views vừa phải có thể vượt KOL có views rất cao nhưng ER thấp

**So sánh:**
- 10,000 views → log = 4.0
- 100,000 views → log = 5.0 (chỉ tăng 25%)
- 1,000,000 views → log = 6.0 (chỉ tăng thêm 20%)

→ Views tăng 100 lần nhưng score chỉ tăng 1.5 lần, giúp ER% có trọng số lớn hơn
- KOL B: 50,000 views × 8% ER = 50,000 × 0.08 = 4,000 score
- KOL C: 200,000 views × 2% ER = 200,000 × 0.02 = 4,000 score
- **Xếp hạng: A > B = C**

**Lý do sử dụng công thức này:**
- Cân bằng giữa Reach (lượt xem) và Quality (tỷ lệ tương tác)
- KOL có nhiều views nhưng ER thấp vẫn có giá trị
- KOL có ít views nhưng ER cao cũng được đánh giá tốt
- Score cao = Cả views lẫn ER đều tốt

**Lưu ý:**
- Engagement Rate được tính cho từng video
- Avg Engagement Rate của KOL = Tổng Engagement / Tổng Views × 100%
- KOL được xếp hạng theo Score = Views × (ER% / 100)

## Cấu trúc Google Sheets

Tạo một sheet với tên `KOL_management` có các cột sau:

| Cột | Mô tả | Ví dụ |
|-----|-------|-------|
| TIKTOK ACCOUNT | Tên tài khoản TikTok | @username |
| LINK TIKTOK | Link profile TikTok | https://www.tiktok.com/@username |
| SẢN PHẨM | Tên sản phẩm đã book | Máy sấy tóc ABC |
| LINK BÀI ĐĂNG | Link các video đã đăng (mỗi link một dòng hoặc phân cách bằng dấu phẩy) | https://www.tiktok.com/@username/video/123 |

## Cài đặt

### Backend

```bash
cd backend-data
pip install requests gspread

# Cấu hình .env
echo "KOL_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit" >> .env
echo "N8N_WEBHOOK_URL=https://your-n8n-domain.com/webhook/tiktok-stats" >> .env

# Chạy backend
python app.py
```

### Frontend

```bash
cd frontend-base
npm install
npm run dev
```

## Sử dụng

### 1. Truy cập trang Quản lý KOL

Mở: `http://localhost:3000/kol-management`

### 2. Đồng bộ dữ liệu

- Nhập URL Google Sheet (hoặc sử dụng URL mặc định)
- Click "Đồng bộ" để lấy danh sách KOL

### 3. Xem bảng quản lý

Tab "Quản lý KOL" hiển thị:
- Tên TikTok account
- Sản phẩm đã book
- Số bài đăng
- Trạng thái (Đã đăng / Chưa đăng)
- Link các bài đăng

### 4. Xem bảng xếp hạng

- Chuyển sang tab "Bảng xếp hạng"
- Click "Tải bảng xếp hạng"
- Hệ thống sẽ:
  - Lấy dữ liệu từ Google Sheets
  - Gọi n8n để lấy stats từ TikTok
  - Tính toán engagement
  - Xếp hạng KOL

Bảng xếp hạng hiển thị:
- Hạng (🥇🥈🥉 cho top 3)
- Lượt xem, Likes, Comments, Shares
- Tổng Engagement
- Tỷ lệ tương tác (%)

## Lưu ý

1. **n8n Webhook**: Cần setup n8n workflow trước (xem `backend-data/kol_management/N8N_SETUP_GUIDE.md`)
2. **Google Service Account**: Cần chia sẻ Sheet với service account email
3. **Tốc độ**: Mỗi video mất ~2-3 giây để lấy stats
4. **Rate Limiting**: Không nên crawl quá nhiều video cùng lúc

## Troubleshooting

### Không lấy được stats

1. Kiểm tra n8n workflow đã activate chưa
2. Test n8n webhook trực tiếp
3. Xem execution history trong n8n UI

### Không đọc được Google Sheets

1. Kiểm tra service account có quyền truy cập
2. Kiểm tra sheet name đúng chưa
3. Kiểm tra credentials file tồn tại

## API Documentation

Chi tiết API: `backend-data/API_GUIDE.md`
