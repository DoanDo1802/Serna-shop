# Hướng dẫn sử dụng API

## Khởi động Backend

```bash
cd backend-data
source venv/bin/activate
python3 app.py
```

Server chạy tại: `http://localhost:5000`

---

## API Endpoints

### 1. Health Check
Kiểm tra server đang chạy

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "ok",
  "message": "Backend đang hoạt động"
}
```

---

### 2. Export dữ liệu Kalodata

**Endpoint:** `POST /api/kalodata/export`

**Body:**
```json
{
  "start_date": "2026-02-14",
  "end_date": "2026-03-14",
  "revenue_min": 50000000,
  "revenue_max": 100000000,
  "age_range": "25-34",
  "page_size": 10
}
```

**Ví dụ:**
```bash
curl -X POST http://localhost:5000/api/kalodata/export \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2026-02-14",
    "end_date": "2026-03-14",
    "revenue_min": 50000000,
    "revenue_max": 100000000,
    "age_range": "25-34",
    "page_size": 10
  }'
```

**Response:**
```json
{
  "success": true,
  "file_path": "kalodata/exports/export_kalodata_20260314_120000.xlsx"
}
```

---

### 3. Upload lên Google Sheets

**Endpoint:** `POST /api/kalodata/upload`

**Body:**
```json
{
  "excel_path": "kalodata/exports/export_kalodata_20260314_120000.xlsx",
  "google_sheet_url": "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit",
  "sheet_name": "Sheet1"
}
```

**Ví dụ:**
```bash
curl -X POST http://localhost:5000/api/kalodata/upload \
  -H "Content-Type: application/json" \
  -d '{
    "excel_path": "kalodata/exports/export_kalodata_20260314_120000.xlsx",
    "google_sheet_url": "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
  }'
```

---

### 4. Lấy video TikTok

**Endpoint:** `POST /api/tiktok/videos`

**Body:**
```json
{
  "profile_url": "https://www.tiktok.com/@username"
}
```

**Ví dụ:**
```bash
curl -X POST http://localhost:5000/api/tiktok/videos \
  -H "Content-Type: application/json" \
  -d '{"profile_url": "https://www.tiktok.com/@cohocchamda"}'
```

**Response:**
```json
{
  "success": true,
  "videos": [
    {
      "id": "7476832218036423943",
      "title": "Video title",
      "thumbnail": "https://...",
      "url": "https://www.tiktok.com/@username/video/7476832218036423943"
    }
  ]
}
```

---

### 5. Lấy User ID TikTok

**Endpoint:** `POST /api/tiktok/userid`

**Body:**
```json
{
  "profile_url": "https://www.tiktok.com/@username"
}
```

**Ví dụ:**
```bash
curl -X POST http://localhost:5000/api/tiktok/userid \
  -H "Content-Type: application/json" \
  -d '{"profile_url": "https://www.tiktok.com/@cohocchamda"}'
```

**Response:**
```json
{
  "success": true,
  "user_info": {
    "uid": "7490470195179586561",
    "username": "cohocchamda",
    "nickname": "Cô Học Chậm Đa"
  }
}
```

---

### 6. Gửi tin nhắn TikTok (đơn)

**Endpoint:** `POST /api/tiktok/send-dm`

**Body:**
```json
{
  "profile_url": "https://www.tiktok.com/@username",
  "message": "Xin chào, chúng ta có thể hợp tác không?"
}
```

**Ví dụ:**
```bash
curl -X POST http://localhost:5000/api/tiktok/send-dm \
  -H "Content-Type: application/json" \
  -d '{
    "profile_url": "https://www.tiktok.com/@username",
    "message": "Xin chào!"
  }'
```

**Response:**
```json
{
  "success": true,
  "result": {
    "success": true,
    "message": "Đã gửi tin nhắn thành công"
  }
}
```

---

### 7. Gửi tin nhắn hàng loạt

**Endpoint:** `POST /api/tiktok/batch-dm`

**Body:**
```json
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

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "profile_url": "https://www.tiktok.com/@user1",
      "success": true,
      "result": {"success": true, "message": "Đã gửi tin nhắn thành công"}
    },
    {
      "profile_url": "https://www.tiktok.com/@user2",
      "success": false,
      "error": "Không thể lấy UID"
    }
  ]
}
```

---

## Workflow hoàn chỉnh

### Kịch bản 1: Export và upload Kalodata

```bash
# 1. Export dữ liệu
curl -X POST http://localhost:5000/api/kalodata/export \
  -H "Content-Type: application/json" \
  -d '{"page_size": 20}' > response.json

# 2. Lấy file_path từ response
FILE_PATH=$(cat response.json | python3 -c "import sys, json; print(json.load(sys.stdin)['file_path'])")

# 3. Upload lên Google Sheets
curl -X POST http://localhost:5000/api/kalodata/upload \
  -H "Content-Type: application/json" \
  -d "{\"excel_path\": \"$FILE_PATH\", \"google_sheet_url\": \"YOUR_SHEET_URL\"}"
```

### Kịch bản 2: Gửi tin nhắn TikTok tự động

```bash
# 1. Lấy danh sách video
curl -X POST http://localhost:5000/api/tiktok/videos \
  -H "Content-Type: application/json" \
  -d '{"profile_url": "https://www.tiktok.com/@username"}'

# 2. Gửi tin nhắn
curl -X POST http://localhost:5000/api/tiktok/send-dm \
  -H "Content-Type: application/json" \
  -d '{
    "profile_url": "https://www.tiktok.com/@username",
    "message": "Chào bạn, mình thấy video của bạn rất hay!"
  }'
```

---

## Tích hợp với Frontend

### React/Next.js Example

```typescript
// api/kalodata.ts
export async function exportKalodata(params: {
  start_date?: string;
  end_date?: string;
  revenue_min?: number;
  revenue_max?: number;
  age_range?: string;
  page_size?: number;
}) {
  const response = await fetch('http://localhost:5000/api/kalodata/export', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  return response.json();
}

export async function uploadToSheets(excelPath: string, sheetUrl: string) {
  const response = await fetch('http://localhost:5000/api/kalodata/upload', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      excel_path: excelPath,
      google_sheet_url: sheetUrl
    })
  });
  return response.json();
}

// api/tiktok.ts
export async function getTikTokVideos(profileUrl: string) {
  const response = await fetch('http://localhost:5000/api/tiktok/videos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile_url: profileUrl })
  });
  return response.json();
}

export async function sendTikTokDM(profileUrl: string, message: string) {
  const response = await fetch('http://localhost:5000/api/tiktok/send-dm', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile_url: profileUrl, message })
  });
  return response.json();
}
```

### Component Example

```tsx
'use client';

import { useState } from 'react';
import { exportKalodata, uploadToSheets } from '@/api/kalodata';

export function KalodataExporter() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleExport = async () => {
    setLoading(true);
    try {
      // Export
      const exportResult = await exportKalodata({
        page_size: 20,
        age_range: "25-34"
      });
      
      if (exportResult.success) {
        // Upload
        const uploadResult = await uploadToSheets(
          exportResult.file_path,
          process.env.NEXT_PUBLIC_GOOGLE_SHEET_URL!
        );
        setResult(uploadResult);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button onClick={handleExport} disabled={loading}>
      {loading ? 'Đang xử lý...' : 'Export Kalodata'}
    </button>
  );
}
```

---

## Lưu ý

1. **CORS**: Backend đã bật CORS, frontend có thể gọi từ bất kỳ domain nào
2. **Cookie**: Cần cấu hình cookie Kalodata và TikTok trong file `.env`
3. **Headless**: Playwright chạy ở chế độ headless=True, không hiện cửa sổ browser
4. **Timeout**: Các API có thể mất vài phút để hoàn thành (đặc biệt là export Kalodata)
5. **Rate Limiting**: Tránh gọi quá nhiều request cùng lúc

---

## Cookie Management APIs

### 1. Kiểm tra trạng thái Cookie

**Endpoint:** `GET /api/cookies/status`

**Response:**
```json
{
  "success": true,
  "status": {
    "kalodata": {
      "exists": true,
      "valid": true,
      "updated_at": "2026-03-22T10:30:00",
      "source": "auto"
    },
    "tiktok": {
      "exists": true,
      "valid": true,
      "updated_at": "2026-03-22T10:30:00",
      "source": "auto"
    }
  }
}
```

**Ví dụ:**
```bash
curl http://localhost:5000/api/cookies/status
```

### 2. Refresh Cookie tự động

**Endpoint:** `POST /api/cookies/refresh`

**Body:**
```json
{
  "platform": "kalodata",  // "kalodata" | "tiktok" | "all"
  "force": false           // true = bắt buộc lấy mới
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "kalodata": {
      "success": true,
      "message": "Cookie Kalodata đã được cập nhật",
      "length": 2500
    }
  }
}
```

**Ví dụ:**
```bash
# Refresh Kalodata cookie
curl -X POST http://localhost:5000/api/cookies/refresh \
  -H "Content-Type: application/json" \
  -d '{"platform": "kalodata", "force": false}'

# Refresh tất cả cookies
curl -X POST http://localhost:5000/api/cookies/refresh \
  -H "Content-Type: application/json" \
  -d '{"platform": "all", "force": false}'

# Force refresh TikTok
curl -X POST http://localhost:5000/api/cookies/refresh \
  -H "Content-Type: application/json" \
  -d '{"platform": "tiktok", "force": true}'
```

**Lưu ý:**
- Lần đầu tiên sẽ mở trình duyệt để bạn đăng nhập
- Các lần sau sẽ tự động dùng cookie cũ (không cần login)
- `force: true` sẽ bắt buộc lấy cookie mới

---

## Troubleshooting

### Lỗi "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Lỗi "Cookie hết hạn"
- **Cách tự động (Khuyến nghị):** Dùng API `/api/cookies/refresh` hoặc Settings page trên frontend
- **Cách thủ công:** Cập nhật cookie mới trong file `.env`

### Lỗi "Google Sheets Permission"
- Chia sẻ Sheet với email service account (quyền Editor)

### API không response
- Kiểm tra server đang chạy: `curl http://localhost:5000/health`
- Xem log trong terminal
