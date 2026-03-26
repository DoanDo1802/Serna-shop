# TikTok Cookie - Hướng Dẫn Lấy Thủ Công

Nếu script tự động không hoạt động do TikTok block, bạn có thể lấy cookie thủ công.

## 🔧 Cách 1: Copy Cookie Từ Trình Duyệt (Nhanh Nhất)

### Bước 1: Mở TikTok trên trình duyệt thường
1. Mở Chrome/Firefox/Safari
2. Truy cập: https://www.tiktok.com
3. Đăng nhập vào tài khoản của bạn

### Bước 2: Mở DevTools
- **Chrome/Edge**: `F12` hoặc `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
- **Firefox**: `F12` hoặc `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
- **Safari**: `Cmd+Option+I` (cần bật Developer menu trước)

### Bước 3: Copy Cookie
1. Vào tab **Application** (Chrome) hoặc **Storage** (Firefox)
2. Bên trái, click **Cookies** → **https://www.tiktok.com**
3. Bạn sẽ thấy danh sách cookies

### Bước 4: Export Cookie String

#### Option A: Dùng Console (Dễ nhất)
1. Vào tab **Console** trong DevTools
2. Paste đoạn code này và nhấn Enter:

```javascript
copy(document.cookie)
```

3. Cookie đã được copy vào clipboard!

#### Option B: Copy thủ công
1. Trong tab Cookies, copy từng cookie theo format:
   ```
   name1=value1; name2=value2; name3=value3
   ```

### Bước 5: Lưu Cookie

#### Option 1: Vào file .env
```bash
cd backend-data
nano .env
```

Tìm dòng `TIKTOK_COOKIE=` và paste cookie vào:
```
TIKTOK_COOKIE=delay_guest_mode_vid=8; passport_csrf_token=abc123...
```

#### Option 2: Vào file .tiktok_cookie
```bash
cd backend-data/tiktok
nano .tiktok_cookie
```

Paste cookie vào và save.

### Bước 6: Convert sang JSON
```bash
cd backend-data
python3 fix_tiktok_cookie.py
```

### Bước 7: Restart Backend
```bash
# Stop backend (Ctrl+C)
python3 app.py
```

### Bước 8: Kiểm tra
```bash
python3 test_cookie_status.py
```

Hoặc reload Settings page: http://localhost:3000/settings

---

## 🔧 Cách 2: Dùng Extension (Tự động hơn)

### Bước 1: Cài Extension
- Chrome: [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
- Firefox: [Cookie-Editor](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)

### Bước 2: Export Cookie
1. Mở TikTok và đăng nhập
2. Click icon extension
3. Click "Export" → Copy cookie string

### Bước 3: Lưu vào .env
Giống Cách 1, Bước 5

---

## 🔧 Cách 3: Dùng curl (Advanced)

```bash
# Lấy cookie từ request
curl -I https://www.tiktok.com -c cookies.txt

# Xem cookie
cat cookies.txt
```

---

## ⚠️ Lưu Ý

### Cookie Quan Trọng
TikTok cần các cookies này để hoạt động:
- `sessionid` - Session ID (quan trọng nhất)
- `sid_tt` - Session token
- `uid_tt` - User ID
- `cmpl_token` - Complete token

### Cookie Hết Hạn
- Cookie TikTok thường hết hạn sau 1-2 tuần
- Khi hết hạn, lặp lại các bước trên

### Security
- ⚠️ **KHÔNG** share cookie với người khác
- ⚠️ **KHÔNG** commit cookie vào Git
- ⚠️ Cookie = quyền truy cập tài khoản của bạn

---

## 🐛 Troubleshooting

### Cookie không hoạt động
1. Đảm bảo copy đầy đủ (không bị cắt)
2. Không có ký tự xuống dòng
3. Format đúng: `name=value; name2=value2`

### Vẫn bị lỗi
```bash
# Xóa cookie cũ
rm backend-data/tiktok/.tiktok_cookie*

# Lấy lại từ đầu
```

### TikTok vẫn block
- Thử dùng VPN
- Thử trình duyệt khác
- Thử từ máy/mạng khác

---

## 💡 Tips

### Kiểm tra Cookie Valid
```bash
cd backend-data
python3 test_cookie_status.py
```

### Update Cookie nhanh
```bash
# Edit .env
nano .env

# Convert to JSON
python3 fix_tiktok_cookie.py

# Restart backend
# Ctrl+C rồi python3 app.py
```

### Tự động hóa (sau khi có cookie)
Sau khi lấy cookie thủ công 1 lần, script tự động sẽ hoạt động:
```bash
python3 update_cookies.py --tiktok
```

---

## 📞 Khi Nào Cần Lấy Thủ Công?

**Cần:**
- ✅ TikTok block script tự động
- ✅ Lần đầu tiên setup
- ✅ Đổi tài khoản TikTok

**Không cần:**
- ❌ Cookie còn hạn
- ❌ Script tự động hoạt động tốt
- ❌ Chỉ muốn refresh cookie

---

## 🎯 So Sánh

| Cách | Thời gian | Độ khó | Khi nào dùng |
|------|-----------|--------|--------------|
| **Tự động** | 30s | Dễ | Khi script hoạt động |
| **Thủ công** | 2-3 phút | Trung bình | Khi TikTok block |
| **Extension** | 1 phút | Dễ | Nếu có extension |

---

**Khuyến nghị:** Thử script tự động trước. Nếu không được, dùng cách thủ công.
