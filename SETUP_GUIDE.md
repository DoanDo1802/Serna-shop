# Hướng dẫn Setup và Chạy Hệ thống KOL Data

## Tổng quan

Hệ thống gồm 2 phần:
- **Backend**: Flask API (Python) - Crawl dữ liệu từ Kalodata và TikTok
- **Frontend**: Next.js (React/TypeScript) - Giao diện quản lý dữ liệu

---

## 1. Setup Backend

### Bước 1: Cài đặt dependencies

```bash
cd backend-data
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### Bước 2: Cấu hình Cookie

Tạo file `.env`:

```bash
cp .env.example .env
```

Chỉnh sửa `.env` và thêm cookie:

```env
PORT=5000
KALODATA_COOKIE=your_kalodata_cookie_here
TIKTOK_COOKIE=your_tiktok_cookie_here
```

**Cách lấy cookie:**

1. Đăng nhập vào Kalodata/TikTok trên Chrome
2. Mở DevTools (F12) → Tab Application → Cookies
3. Copy toàn bộ cookies thành chuỗi: `name1=value1; name2=value2; ...`
4. Paste vào file `.env`

### Bước 3: Chạy Backend

```bash
source venv/bin/activate
python3 app.py
```

Backend sẽ chạy tại: `http://localhost:5000`

Test backend:
```bash
curl http://localhost:5000/health
```

---

## 2. Setup Frontend

### Bước 1: Cài đặt dependencies

```bash
cd frontend-base
npm install
# hoặc
yarn install
# hoặc
pnpm install
```

### Bước 2: Cấu hình API URL

File `.env.local` đã được tạo sẵn:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### Bước 3: Chạy Frontend

```bash
npm run dev
# hoặc
yarn dev
# hoặc
pnpm dev
```

Frontend sẽ chạy tại: `http://localhost:3000`

---

## 3. Sử dụng Hệ thống

### Crawl dữ liệu KOL

1. Mở trình duyệt: `http://localhost:3000`
2. Nhấn nút **"Crawl dữ liệu"**
3. Đợi vài phút để hệ thống crawl từ Kalodata
4. Dữ liệu sẽ hiển thị trong bảng

### Tính năng

- ✅ Crawl dữ liệu KOL từ Kalodata
- ✅ Hiển thị dữ liệu trong bảng
- ✅ Tìm kiếm theo tên
- ✅ Sắp xếp theo cột
- ✅ Xuất dữ liệu ra CSV
- ✅ Link trực tiếp đến Kalodata

---

## 4. Cấu trúc Thư mục

```
data-kol/
├── backend-data/              # Backend Flask API
│   ├── app.py                # Main API server
│   ├── kalodata/             # Module Kalodata
│   │   ├── exp_playwright_api.py  # Export API
│   │   └── ...
│   ├── tiktok/               # Module TikTok
│   │   ├── tiktok.py         # Get videos
│   │   ├── dmtiktok.py       # Send DM
│   │   └── ...
│   ├── .env                  # Config (không commit)
│   └── requirements.txt      # Python dependencies
│
└── frontend-base/            # Frontend Next.js
    ├── app/                  # Next.js app directory
    ├── components/           # React components
    │   └── data-table.tsx    # Bảng dữ liệu chính
    ├── lib/
    │   └── api.ts            # API client
    ├── .env.local            # Frontend config
    └── package.json          # Node dependencies
```

---

## 5. API Endpoints

### Backend APIs

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/health` | GET | Health check |
| `/api/kalodata/export` | POST | Crawl dữ liệu Kalodata |
| `/api/kalodata/upload` | POST | Upload lên Google Sheets |
| `/api/tiktok/videos` | POST | Lấy video TikTok |
| `/api/tiktok/userid` | POST | Lấy User ID TikTok |
| `/api/tiktok/send-dm` | POST | Gửi tin nhắn TikTok |
| `/api/tiktok/batch-dm` | POST | Gửi tin nhắn hàng loạt |

Chi tiết xem file: `backend-data/API_GUIDE.md`

---

## 6. Troubleshooting

### Backend không chạy

**Lỗi: ModuleNotFoundError**
```bash
cd backend-data
source venv/bin/activate
pip install -r requirements.txt
```

**Lỗi: Cookie hết hạn**
- Đăng nhập lại Kalodata/TikTok
- Copy cookie mới vào `.env`

**Lỗi: Playwright browser not found**
```bash
playwright install chromium
```

### Frontend không kết nối Backend

**Kiểm tra Backend đang chạy:**
```bash
curl http://localhost:5000/health
```

**Kiểm tra CORS:**
- Backend đã bật CORS cho tất cả origins
- Nếu vẫn lỗi, kiểm tra console browser

**Kiểm tra API URL:**
- File `.env.local` có đúng URL backend không
- Restart frontend sau khi sửa `.env.local`

### Crawl dữ liệu lâu

- Kalodata export có thể mất 2-5 phút
- Đợi cho đến khi có thông báo thành công
- Không refresh trang trong lúc crawl

---

## 7. Development Tips

### Chạy cả Backend và Frontend

**Terminal 1 - Backend:**
```bash
cd backend-data
source venv/bin/activate
python3 app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend-base
npm run dev
```

### Debug Backend

Xem log trong terminal chạy `python3 app.py`

### Debug Frontend

Mở DevTools (F12) → Console → Network tab

---

## 8. Production Deployment

### Backend

```bash
# Sử dụng gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend

```bash
npm run build
npm start
```

### Environment Variables

**Backend (.env):**
- `PORT`: Port cho Flask server
- `KALODATA_COOKIE`: Cookie Kalodata
- `TIKTOK_COOKIE`: Cookie TikTok

**Frontend (.env.local):**
- `NEXT_PUBLIC_API_URL`: URL của backend API

---

## 9. Roadmap

- [ ] Thêm filter nâng cao (doanh thu, độ tuổi, giới tính)
- [ ] Pagination cho bảng dữ liệu
- [ ] Lưu dữ liệu vào database
- [ ] Tích hợp gửi tin nhắn TikTok từ giao diện
- [ ] Dashboard analytics
- [ ] Export nhiều format (Excel, JSON)
- [ ] Scheduled crawl (cron job)

---

## 10. Support

Nếu gặp vấn đề, kiểm tra:
1. Backend log (terminal chạy `python3 app.py`)
2. Frontend console (DevTools → Console)
3. Network requests (DevTools → Network)
4. Cookie còn hạn không

---

**Chúc bạn sử dụng hệ thống thành công! 🚀**
