# 📝 Hướng Dẫn Nhập Cookie Thủ Công

## Tại Sao Cần Nhập Thủ Công?

- ✅ TikTok/Kalodata đang block script tự động
- ✅ Muốn đổi tài khoản
- ✅ Cookie hết hạn
- ✅ Đơn giản và luôn hoạt động

---

## 🚀 Quy Trình (3 Phút)

### Bước 1: Lấy Cookie Từ Trình Duyệt

1. **Mở trình duyệt thường** (Chrome/Firefox/Safari)
2. **Truy cập:**
   - TikTok: https://www.tiktok.com
   - Kalodata: https://www.kalodata.com
3. **Đăng nhập** tài khoản bạn muốn dùng
4. **Mở DevTools:**
   - Windows: `F12` hoặc `Ctrl+Shift+I`
   - Mac: `Cmd+Option+I`
5. **Chọn tab "Console"**
6. **Paste dòng này và nhấn Enter:**
   ```javascript
   copy(document.cookie)
   ```
7. **Cookie đã được copy!** ✅

### Bước 2: Nhập Vào Settings

1. **Vào Settings page:**
   ```
   http://localhost:3000/settings
   ```

2. **Tìm card platform** (TikTok hoặc Kalodata)

3. **Click nút "Nhập cookie mới"** (có icon bút ✏️)

4. **Paste cookie** vào ô textarea (Ctrl+V / Cmd+V)

5. **Click "Lưu Cookie"**

6. **Thấy thông báo:**
   ```
   ✅ Đã lưu cookie tiktok thành công! (63 cookies)
   ```

7. **Xong!** Status chuyển sang 🟢 Hợp lệ

---

## 📸 Screenshot Guide

### 1. Mở Console
```
Chrome: F12 → Tab "Console"
Firefox: F12 → Tab "Console"  
Safari: Cmd+Option+I → Tab "Console"
```

### 2. Copy Cookie
```
Console > copy(document.cookie) > Enter
```

### 3. Paste Vào Settings
```
Settings > Nhập cookie mới > Paste > Lưu
```

---

## 💡 Tips

### Kiểm Tra Cookie Hợp Lệ
- Sau khi paste, xem "Số ký tự" ở dưới ô
- Cookie hợp lệ thường > 1000 ký tự
- TikTok: ~5000-7000 ký tự
- Kalodata: ~1500-2000 ký tự

### Cookie Không Hoạt Động?
1. Đảm bảo đã đăng nhập trước khi copy
2. Copy lại từ đầu
3. Thử trình duyệt khác
4. Clear cache và đăng nhập lại

### Đổi Tài Khoản
1. Logout tài khoản cũ trên trình duyệt
2. Login tài khoản mới
3. Copy cookie mới
4. Paste vào Settings
5. Xong!

---

## 🔄 So Sánh: Script vs Thủ Công

| | Script Tự Động | Nhập Thủ Công |
|---|----------------|---------------|
| **Thời gian** | 30s-2 phút | 1-2 phút |
| **Độ khó** | Dễ | Rất dễ |
| **Khi TikTok block** | ❌ Không hoạt động | ✅ Luôn hoạt động |
| **Đổi tài khoản** | Khó | Dễ |
| **Cần terminal** | ✅ Có | ❌ Không |
| **Khuyến nghị** | Khi script hoạt động | **Khi TikTok block** ⭐ |

---

## ⚠️ Lưu Ý Bảo Mật

### KHÔNG Làm:
- ❌ Share cookie với người khác
- ❌ Paste cookie vào website lạ
- ❌ Commit cookie vào Git
- ❌ Screenshot cookie và share

### NÊN Làm:
- ✅ Chỉ paste vào Settings page của bạn
- ✅ Đổi cookie định kỳ (1-2 tuần)
- ✅ Logout khi không dùng
- ✅ Dùng tài khoản riêng cho automation

---

## 🐛 Troubleshooting

### "Cookie quá ngắn hoặc không hợp lệ"
- Cookie phải > 50 ký tự
- Kiểm tra đã copy đầy đủ chưa
- Thử copy lại

### "Không thể lưu cookie"
- Check backend đang chạy: http://localhost:5000/health
- Xem log terminal backend
- Restart backend

### Status vẫn "Không hợp lệ"
- Click "Kiểm tra" để refresh status
- Reload Settings page
- Chạy: `python3 test_cookie_status.py`

---

## 📞 Khi Nào Dùng?

### Dùng "Nhập cookie mới":
- ✅ TikTok báo "Maximum attempts"
- ✅ Muốn đổi tài khoản
- ✅ Cookie hết hạn
- ✅ Script tự động không hoạt động

### Dùng "Kiểm tra":
- ✅ Xem cookie còn hạn không
- ✅ Validate cookie hiện tại
- ✅ Không cần thay đổi gì

---

**Tóm lại:** Nhập thủ công đơn giản, nhanh, và luôn hoạt động! 🎉
