# 🍪 Cookie Management Feature - Complete Guide

## 📋 Tổng Quan

Feature quản lý cookie tự động cho Kalodata và TikTok, bao gồm:
- ✅ Backend API để refresh cookie
- ✅ Frontend Settings page để quản lý
- ✅ Tự động phát hiện cookie hết hạn
- ✅ Chỉ cần đăng nhập 1 lần

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Settings Page (/settings)                    │  │
│  │  - Cookie status dashboard                           │  │
│  │  - Refresh buttons                                   │  │
│  │  - Real-time status updates                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           │ HTTP API                        │
│                           ▼                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Flask)                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                       │  │
│  │  - GET  /api/cookies/status                          │  │
│  │  - POST /api/cookies/refresh                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Auto Cookie Scripts                                 │  │
│  │  - kalodata/auto_cookie.py                           │  │
│  │  - tiktok/auto_cookie.py                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Playwright Browser Automation                       │  │
│  │  - Open browser                                      │  │
│  │  - Load old cookies                                  │  │
│  │  - Check login status                                │  │
│  │  - Get new cookies                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Cookie Storage                                      │  │
│  │  - .cookie / .tiktok_cookie (text)                   │  │
│  │  - .cookie.json / .tiktok_cookie.json (metadata)     │  │
│  │  - .env (auto-updated)                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Files Created/Modified

### Backend Files

#### New Files
```
backend-data/
├── kalodata/
│   ├── auto_cookie.py              # Auto cookie logic for Kalodata
│   ├── .cookie.json                # Cookie storage with metadata
│   └── .cookie                     # Cookie text format
├── tiktok/
│   ├── auto_cookie.py              # Auto cookie logic for TikTok
│   ├── .tiktok_cookie.json         # Cookie storage with metadata
│   └── .tiktok_cookie              # Cookie text format
├── update_cookies.py               # CLI script to update cookies
├── setup_cookies.sh                # Setup script for first time
├── COOKIE_GUIDE.md                 # Detailed guide
├── QUICK_START.md                  # Quick reference
└── AUTO_COOKIE_SUMMARY.md          # Technical summary
```

#### Modified Files
```
backend-data/
├── app.py                          # Added cookie management APIs
├── README.md                       # Added auto cookie instructions
├── API_GUIDE.md                    # Added cookie API docs
└── .gitignore                      # Added .cookie.json files
```

### Frontend Files

#### New Files
```
frontend-base/
└── app/
    └── settings/
        ├── page.tsx                # Settings page UI
        └── README.md               # Settings page docs
```

#### Modified Files
```
frontend-base/
└── components/
    └── sidebar.tsx                 # Added Settings link
```

---

## 🚀 Usage

### For End Users (Frontend)

1. **Mở Settings Page**
   - Click "Cài đặt" ở sidebar
   - Hoặc truy cập: `http://localhost:3000/settings`

2. **Xem Trạng Thái Cookie**
   - 🟢 Hợp lệ: Cookie đang hoạt động
   - 🔴 Chưa có: Chưa có cookie
   - ⚪ Không hợp lệ: Cookie có vấn đề

3. **Refresh Cookie**
   - Click "Làm mới" để kiểm tra và cập nhật
   - Click "Force" để bắt buộc lấy mới

4. **Lần Đầu Tiên**
   - Click "Làm mới"
   - Trình duyệt sẽ mở
   - Đăng nhập thủ công
   - Cookie được lưu tự động

5. **Lần Sau**
   - Click "Làm mới"
   - Hệ thống tự động dùng cookie cũ
   - Không cần login lại

### For Developers (CLI)

```bash
# Setup lần đầu
cd backend-data
bash setup_cookies.sh

# Update cookies
python3 update_cookies.py

# Update chỉ Kalodata
python3 update_cookies.py --kalodata

# Update chỉ TikTok
python3 update_cookies.py --tiktok

# Force refresh
python3 update_cookies.py --force
```

### For API Integration

```bash
# Check status
curl http://localhost:5000/api/cookies/status

# Refresh Kalodata
curl -X POST http://localhost:5000/api/cookies/refresh \
  -H "Content-Type: application/json" \
  -d '{"platform": "kalodata", "force": false}'

# Refresh all
curl -X POST http://localhost:5000/api/cookies/refresh \
  -H "Content-Type: application/json" \
  -d '{"platform": "all", "force": false}'
```

---

## 🔧 Technical Details

### Backend API Endpoints

#### 1. GET /api/cookies/status
Returns current cookie status for both platforms.

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

#### 2. POST /api/cookies/refresh
Refresh cookies for specified platform(s).

**Request:**
```json
{
  "platform": "kalodata",  // "kalodata" | "tiktok" | "all"
  "force": false           // true = force new cookie
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

### Cookie Validation Logic

```python
def is_cookie_valid(cookies):
    # Check important cookies exist
    important_cookies = ["SESSION", "sid_guard"]
    
    # Check expiry
    for cookie in cookies:
        if cookie.get("expires", -1) < now():
            return False
    
    return True
```

### Cookie Storage Format

**Text Format (.cookie):**
```
name1=value1; name2=value2; name3=value3; ...
```

**JSON Format (.cookie.json):**
```json
{
  "cookies": [
    {
      "name": "SESSION",
      "value": "abc123...",
      "domain": ".kalodata.com",
      "path": "/",
      "expires": 1234567890
    }
  ],
  "updated_at": "2026-03-22T10:30:00"
}
```

---

## 🎨 Frontend UI

### Components Used
- `Card` - Container for each platform
- `Button` - Action buttons
- `Badge` - Status indicators
- `Alert` - Success/error messages
- `RefreshCw` - Loading spinner icon

### Status Indicators
- 🟢 **Hợp lệ** (Green badge)
- 🔴 **Chưa có** (Red badge)
- ⚪ **Không hợp lệ** (Gray badge)

### Source Indicators
- 🤖 **Tự động** - From auto script
- 📝 **Thủ công** - From .env file

---

## 🔄 User Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ User opens Settings page                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Frontend fetches cookie status from API                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Display status: Valid / Invalid / Not Found                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ User clicks "Làm mới" or "Force"                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Frontend calls /api/cookies/refresh                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Backend checks old cookie validity                          │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ Cookie valid?    │    │ Cookie invalid?  │
│ → Use old cookie │    │ → Get new cookie │
└──────────────────┘    └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │ Open browser     │
                        │ User logs in     │
                        │ Save new cookie  │
                        └────────┬─────────┘
                                 │
         ┌───────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Update .env file with new cookie                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Return success to frontend                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Frontend shows success message & refreshes status           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Benefits

### Before (Manual)
- ❌ Copy cookie từ DevTools thủ công
- ❌ Cookie hết hạn → Phải copy lại
- ❌ Mất 5-10 phút mỗi lần
- ❌ Dễ quên hoặc nhầm lẫn

### After (Auto)
- ✅ 1 click để refresh cookie
- ✅ Tự động phát hiện hết hạn
- ✅ Chỉ login 1 lần duy nhất
- ✅ Mất 30 giây
- ✅ UI trực quan, dễ sử dụng

---

## 🛠️ Troubleshooting

### Frontend Issues

**Error: "Không thể kết nối đến backend"**
- Check backend đang chạy: `curl http://localhost:5000/health`
- Check CORS settings

**Cookie status không update**
- Click refresh button
- Check browser console for errors

### Backend Issues

**Error: "Playwright not installed"**
```bash
pip install playwright
playwright install chromium
```

**Error: "Cookie không hợp lệ"**
- Click "Force" để lấy cookie mới
- Đăng nhập lại khi được yêu cầu

**Browser không mở**
- Check Playwright installed
- Try with `headless=False`

---

## 🔮 Future Enhancements

### Phase 2
- [ ] Auto-refresh timer (countdown)
- [ ] Cookie expiry prediction
- [ ] Email notification when cookie expires
- [ ] Cookie history/logs

### Phase 3
- [ ] Manual cookie input option
- [ ] Test cookie validity button
- [ ] Multiple account support
- [ ] Cookie encryption

### Phase 4
- [ ] Scheduled auto-refresh (cronjob)
- [ ] Cookie health monitoring
- [ ] Analytics dashboard
- [ ] API rate limiting

---

## 📝 Documentation Links

- [COOKIE_GUIDE.md](backend-data/COOKIE_GUIDE.md) - Detailed guide
- [QUICK_START.md](backend-data/QUICK_START.md) - Quick reference
- [AUTO_COOKIE_SUMMARY.md](backend-data/AUTO_COOKIE_SUMMARY.md) - Technical summary
- [API_GUIDE.md](backend-data/API_GUIDE.md) - API documentation
- [Settings README](frontend-base/app/settings/README.md) - Frontend docs

---

## ✅ Checklist

### Backend
- [x] Auto cookie scripts (Kalodata + TikTok)
- [x] API endpoints (/status, /refresh)
- [x] Cookie validation logic
- [x] .env auto-update
- [x] Error handling
- [x] Documentation

### Frontend
- [x] Settings page UI
- [x] Cookie status dashboard
- [x] Refresh buttons
- [x] Loading states
- [x] Error/success alerts
- [x] Sidebar link

### Documentation
- [x] User guide
- [x] API documentation
- [x] Technical summary
- [x] Quick start guide
- [x] Troubleshooting

---

**Tóm lại:** Feature hoàn chỉnh để quản lý cookie tự động, cải thiện UX và tiết kiệm thời gian! 🎉
